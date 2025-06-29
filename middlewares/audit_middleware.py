# middlewares/audit_middleware.py
import json
import time
from datetime import datetime
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from modles.audit_models import AuditTrail
from utils.security import decode_token


class AuditMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, excluded_paths: list = None):
        super().__init__(app)
        # Exclude paths that don't need auditing
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/health"
        ]

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request headers"""
        # Check for forwarded headers (proxy/load balancer)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"

    def get_user_id_from_token(self, request: Request) -> int:
        """Extract user_id from JWT token - same logic as your dependency"""
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None

            token = auth_header.split(" ")[1]
            payload = decode_token(token)
            user_id = payload.get("user_id")
            return user_id
        except Exception:
            # If token is invalid or missing, return None (anonymous user)
            return None

    def should_audit(self, path: str) -> bool:
        """Check if the path should be audited"""
        for excluded_path in self.excluded_paths:
            if path.startswith(excluded_path):
                return False
        return True

    async def get_request_body(self, request: Request) -> str:
        """Safely extract request body"""
        try:
            body = await request.body()
            if body:
                # Try to parse as JSON for better storage
                try:
                    json_body = json.loads(body.decode('utf-8'))
                    # Mask sensitive fields
                    if isinstance(json_body, dict):
                        sensitive_fields = ['password', 'card_number', 'cvv']
                        for field in sensitive_fields:
                            if field in json_body:
                                json_body[field] = "***MASKED***"
                    return json.dumps(json_body)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return body.decode('utf-8', errors='ignore')[:1000]  # Limit size
            return None
        except Exception:
            return None

    async def get_response_body(self, response: Response) -> str:
        """Extract response body from different response types"""
        try:
            if isinstance(response, StreamingResponse):
                # Handle StreamingResponse (most FastAPI responses)
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk

                # Recreate the response with the same body
                response.body_iterator = self.generate_new_body(response_body)

                # Decode and process the body
                body_str = response_body.decode('utf-8')

                # Limit response body size for storage
                if len(body_str) > 5000:  # 5KB limit
                    return body_str[:5000] + "... [TRUNCATED]"
                return body_str

            elif hasattr(response, 'body') and response.body:
                # Handle regular Response objects
                body = response.body.decode('utf-8')
                if len(body) > 5000:
                    return body[:5000] + "... [TRUNCATED]"
                return body
            return None
        except Exception as e:
            print(f"Error extracting response body: {e}")
            return None

    async def generate_new_body(self, body: bytes):
        """Generate new body iterator for streaming response"""
        yield body

    async def dispatch(self, request: Request, call_next):
        # Skip auditing for excluded paths
        if not self.should_audit(request.url.path):
            return await call_next(request)

        # Start timing
        start_time = time.time()

        # Extract request information
        # Get user_id directly from JWT token (same as your dependency logic)
        user_id = self.get_user_id_from_token(request)

        client_ip = self.get_client_ip(request)
        method = request.method
        endpoint = str(request.url.path)
        user_agent = request.headers.get("User-Agent", "")[:512]  # Limit size

        # Get request body (need to cache it since it can only be read once)
        request_body = await self.get_request_body(request)

        # Recreate request body for downstream processing
        if request_body:
            # Create a new receive callable that returns the cached body
            cached_body = request_body.encode() if isinstance(request_body, str) else request_body

            async def receive():
                return {
                    "type": "http.request",
                    "body": cached_body,
                    "more_body": False
                }

            request._receive = receive

        # Process the request
        response_body = None
        try:
            response = await call_next(request)
            response_status = response.status_code

            # Calculate execution time
            execution_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds

            # Extract response body
            response_body = await self.get_response_body(response)

        except Exception as e:
            # Handle errors during request processing
            response_status = 500
            execution_time = int((time.time() - start_time) * 1000)
            response_body = json.dumps({"error": str(e)})

            # Save audit record for error
            await self.save_audit_record(
                user_id, client_ip, method, endpoint, request_body,
                response_body, response_status, user_agent, execution_time
            )
            raise

        # Save audit record to database
        await self.save_audit_record(
            user_id, client_ip, method, endpoint, request_body,
            response_body, response_status, user_agent, execution_time
        )

        return response

    async def save_audit_record(self, user_id, client_ip, method, endpoint,
                                request_body, response_body, response_status,
                                user_agent, execution_time):
        """Save audit record to database"""
        db = SessionLocal()
        try:
            audit_record = AuditTrail(
                user_id=user_id,
                client_ip=client_ip,
                method=method,
                endpoint=endpoint,
                request_body=request_body,
                response_body=response_body,
                response_status=response_status,
                user_agent=user_agent,
                execution_time_ms=execution_time
            )

            db.add(audit_record)
            db.commit()

            # Debug print to verify data
            print(f"Audit saved - User: {user_id}, Endpoint: {endpoint}, Status: {response_status}")

        except Exception as e:
            # Don't let audit failures break the main request
            print(f"Failed to save audit record: {e}")
            db.rollback()
        finally:
            db.close()