"""
Database models and connection management
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Detection(Base):
    """
    Detection model - stores individual detection results
    """
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(String, index=True)
    frame_number = Column(Integer)
    timestamp = Column(Float, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    num_detections = Column(Integer)
    detections = Column(JSON)  # List of detected objects with bbox, confidence, etc.

    def __repr__(self):
        return f"<Detection(stream={self.stream_id}, frame={self.frame_number}, objects={self.num_detections})>"


class StreamInfo(Base):
    """
    Stream information - metadata about video streams
    """
    __tablename__ = "streams"

    id = Column(Integer, primary_key=True, index=True)
    stream_id = Column(String, unique=True, index=True)
    video_source = Column(String)
    status = Column(String)  # 'active', 'stopped', 'error'
    started_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    frames_processed = Column(Integer, default=0)
    total_detections = Column(Integer, default=0)

    def __repr__(self):
        return f"<StreamInfo(id={self.stream_id}, status={self.status})>"


def init_db():
    """
    Initialize database - create all tables
    """
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


def get_db():
    """
    Get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    # Test database connection and create tables
    print("Initializing database...")
    init_db()
    print("✅ Database ready!")