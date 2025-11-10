"""
REST API for Video Analytics System
FastAPI endpoints for querying detections and controlling streams
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import redis

from database import get_db, Detection, StreamInfo
from config import *

app = FastAPI(
    title="Video Analytics API",
    description="Distributed video analytics system with real-time object detection",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection for queue stats
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)


# Pydantic models for request/response
class DetectionResponse(BaseModel):
    id: int
    stream_id: str
    frame_number: int
    timestamp: float
    num_detections: int
    detections: list
    created_at: datetime

    class Config:
        from_attributes = True


class StreamResponse(BaseModel):
    id: int
    stream_id: str
    video_source: str
    status: str
    started_at: datetime
    frames_processed: int
    total_detections: int

    class Config:
        from_attributes = True


class SystemStats(BaseModel):
    total_frames_processed: int
    total_detections: int
    active_streams: int
    frame_queue_size: int
    results_queue_size: int
    total_streams: int


class StreamCreate(BaseModel):
    stream_id: str
    video_source: str


# ============= ENDPOINTS =============

@app.get("/")
def root():
    """API root - health check"""
    return {
        "status": "running",
        "message": "Video Analytics API",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        redis_client.ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"

    return {
        "status": "healthy",
        "redis": redis_status,
        "timestamp": datetime.utcnow()
    }


@app.get("/stats", response_model=SystemStats)
def get_system_stats(db: Session = Depends(get_db)):
    """Get overall system statistics"""

    total_frames = db.query(func.sum(StreamInfo.frames_processed)).scalar() or 0
    total_detections = db.query(func.sum(StreamInfo.total_detections)).scalar() or 0
    active_streams = db.query(StreamInfo).filter(StreamInfo.status == "active").count()
    total_streams = db.query(StreamInfo).count()

    frame_queue_size = redis_client.llen(FRAME_QUEUE)
    results_queue_size = redis_client.llen(RESULTS_QUEUE)

    return SystemStats(
        total_frames_processed=total_frames,
        total_detections=total_detections,
        active_streams=active_streams,
        frame_queue_size=frame_queue_size,
        results_queue_size=results_queue_size,
        total_streams=total_streams
    )


@app.get("/detections", response_model=List[DetectionResponse])
def get_detections(
        stream_id: Optional[str] = None,
        limit: int = Query(default=100, le=1000),
        offset: int = 0,
        db: Session = Depends(get_db)
):
    """
    Get detection results

    - **stream_id**: Filter by stream (optional)
    - **limit**: Number of results (max 1000)
    - **offset**: Pagination offset
    """

    query = db.query(Detection)

    if stream_id:
        query = query.filter(Detection.stream_id == stream_id)

    detections = query.order_by(desc(Detection.timestamp)).offset(offset).limit(limit).all()

    return detections


@app.get("/detections/{detection_id}", response_model=DetectionResponse)
def get_detection(detection_id: int, db: Session = Depends(get_db)):
    """Get a specific detection by ID"""

    detection = db.query(Detection).filter(Detection.id == detection_id).first()

    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")

    return detection


@app.get("/streams", response_model=List[StreamResponse])
def get_streams(
        status: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """
    Get all streams

    - **status**: Filter by status (active/stopped/error)
    """

    query = db.query(StreamInfo)

    if status:
        query = query.filter(StreamInfo.status == status)

    streams = query.all()

    return streams


@app.get("/streams/{stream_id}", response_model=StreamResponse)
def get_stream(stream_id: str, db: Session = Depends(get_db)):
    """Get specific stream information"""

    stream = db.query(StreamInfo).filter(StreamInfo.stream_id == stream_id).first()

    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    return stream


@app.get("/streams/{stream_id}/detections", response_model=List[DetectionResponse])
def get_stream_detections(
        stream_id: str,
        limit: int = Query(default=100, le=1000),
        db: Session = Depends(get_db)
):
    """Get all detections for a specific stream"""

    # Check if stream exists
    stream = db.query(StreamInfo).filter(StreamInfo.stream_id == stream_id).first()
    if not stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    detections = db.query(Detection).filter(
        Detection.stream_id == stream_id
    ).order_by(desc(Detection.timestamp)).limit(limit).all()

    return detections


@app.post("/streams", response_model=StreamResponse)
def create_stream(stream: StreamCreate, db: Session = Depends(get_db)):
    """Register a new stream"""

    # Check if stream already exists
    existing = db.query(StreamInfo).filter(StreamInfo.stream_id == stream.stream_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Stream already exists")

    new_stream = StreamInfo(
        stream_id=stream.stream_id,
        video_source=stream.video_source,
        status="active"
    )

    db.add(new_stream)
    db.commit()
    db.refresh(new_stream)

    return new_stream


@app.get("/queue/stats")
def get_queue_stats():
    """Get Redis queue statistics"""

    return {
        "frame_queue_size": redis_client.llen(FRAME_QUEUE),
        "results_queue_size": redis_client.llen(RESULTS_QUEUE),
        "frame_queue_name": FRAME_QUEUE,
        "results_queue_name": RESULTS_QUEUE
    }


if __name__ == "__main__":
    import uvicorn

    print(f"🚀 Starting API server on http://{API_HOST}:{API_PORT}")
    uvicorn.run(app, host=API_HOST, port=API_PORT)