import os
from datetime import datetime
from sqlalchemy import (Column, String, Integer, Boolean, DateTime, Float,
                        ForeignKey, text)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ---------------------------------------------------------------------------
# Database URL handling (auto‑fix for common URI patterns)
# ---------------------------------------------------------------------------
raw_url = os.getenv(
    "DATABASE_URL",
    os.getenv("POSTGRES_URL", "sqlite:///./app.db")
)
if raw_url.startswith("postgresql+asyncpg://"):
    raw_url = raw_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
elif raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+psycopg://")

# Determine if we need SSL – do not add for localhost or SQLite
connect_args = {}
if not raw_url.startswith("sqlite") and "localhost" not in raw_url:
    connect_args["sslmode"] = "require"

engine = create_engine(raw_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

# ---------------------------------------------------------------------------
# Table name prefix – prevents collisions in shared DBs
# ---------------------------------------------------------------------------
TABLE_PREFIX = "qf_"

class Restaurant(Base):
    __tablename__ = f"{TABLE_PREFIX}restaurants"
    id = Column(String, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String, nullable=False)
    phone = Column(String(20), nullable=False)
    qr_code_url = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    queues = relationship("Queue", back_populates="restaurant")

class Queue(Base):
    __tablename__ = f"{TABLE_PREFIX}queues"
    id = Column(String, primary_key=True)
    restaurant_id = Column(String, ForeignKey(f"{TABLE_PREFIX}restaurants.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)
    current_position = Column(Integer, nullable=False, default=0)
    total_ahead = Column(Integer, nullable=False, default=0)
    estimated_wait_time = Column(Integer, nullable=False, default=0)  # minutes
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    restaurant = relationship("Restaurant", back_populates="queues")
    customers = relationship("Customer", back_populates="queue")
    wait_times = relationship("WaitTime", back_populates="queue")
    ai_estimations = relationship("AIEstimation", back_populates="queue")

class Customer(Base):
    __tablename__ = f"{TABLE_PREFIX}customers"
    id = Column(String, primary_key=True)
    name = Column(String(100))
    phone = Column(String(20), nullable=False)
    email = Column(String(100))
    queue_id = Column(String, ForeignKey(f"{TABLE_PREFIX}queues.id"), nullable=False)
    position_in_queue = Column(Integer, nullable=False, default=0)
    joined_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    notified_at = Column(DateTime)
    seated_at = Column(DateTime)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    queue = relationship("Queue", back_populates="customers")
    wait_times = relationship("WaitTime", back_populates="customer")

class WaitTime(Base):
    __tablename__ = f"{TABLE_PREFIX}wait_times"
    id = Column(String, primary_key=True)
    customer_id = Column(String, ForeignKey(f"{TABLE_PREFIX}customers.id"), nullable=False)
    queue_id = Column(String, ForeignKey(f"{TABLE_PREFIX}queues.id"), nullable=False)
    start_time = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    end_time = Column(DateTime)
    duration = Column(Integer)  # seconds
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    customer = relationship("Customer", back_populates="wait_times")
    queue = relationship("Queue", back_populates="wait_times")

class AIEstimation(Base):
    __tablename__ = f"{TABLE_PREFIX}ai_estimations"
    id = Column(String, primary_key=True)
    queue_id = Column(String, ForeignKey(f"{TABLE_PREFIX}queues.id"), nullable=False)
    estimated_wait_time = Column(Integer, nullable=False)  # minutes
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), onupdate=text('CURRENT_TIMESTAMP'))
    queue = relationship("Queue", back_populates="ai_estimations")

# Create tables if they do not exist (useful for demo environments)
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
