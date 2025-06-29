# models/audit_models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, BigInteger
from sqlalchemy.sql import func
from database import Base


class AuditTrail(Base):
    __tablename__ = "audit_trails"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)  # Nullable for public endpoints
    creation_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    client_ip = Column(String(45), nullable=False)  # IPv6 support (45 chars max)
    method = Column(String(10), nullable=False)  # GET, POST, etc.
    endpoint = Column(String(255), nullable=False)  # Request path
    request_body = Column(Text, nullable=True)  # JSON string of request body
    response_body = Column(Text, nullable=True)  # JSON string of response body
    response_status = Column(Integer, nullable=False)  # HTTP status code
    user_agent = Column(String(512), nullable=True)  # Browser/client info
    execution_time_ms = Column(Integer, nullable=True)  # Request processing time

    def __repr__(self):
        return f"<AuditTrail(id={self.id}, user_id={self.user_id}, endpoint='{self.endpoint}', status={self.response_status})>"