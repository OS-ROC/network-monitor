from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from db import Base

class NetworkMetric(Base):
    __tablename__ = "network_metrics"

    id = Column(Integer, primary_key=True, index=True)
    host = Column(String(50), nullable=False)
    latency_ms = Column(Float)
    packet_loss_percent = Column(Integer)
    http_response_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    host = Column(String(50), nullable=False)

    level = Column(String(20))   # normal / warning / critical
    reason = Column(String(200))

    latency_ms = Column(Float)
    packet_loss_percent = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
    resolved = Column(Integer, default=0)

