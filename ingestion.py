"""
Video Ingestion Service
Reads video frames and pushes them to Redis queue for processing
"""

import cv2
import redis
import time
from config import *
from utils import create_frame_message
from database import SessionLocal, StreamInfo
from datetime import datetime


class VideoIngestion:
    def __init__(self, stream_id: str, video_source=0):
        """
        Initialize video ingestion

        Args:
            stream_id: Unique identifier for this stream
            video_source: 0 for webcam, or path to video file
        """
        self.stream_id = stream_id
        self.video_source = video_source

        # Connect to Redis
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB
        )

        # Test connection
        try:
            self.redis_client.ping()
            print(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        except redis.ConnectionError:
            print("❌ Could not connect to Redis!")
            raise

        # Register stream in database
        self.register_stream()

        # Open video source
        self.cap = cv2.VideoCapture(video_source)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video source: {video_source}")

        # Get video properties
        self.original_fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        print(f"📹 Video source: {video_source}")
        print(f"📐 Resolution: {self.width}x{self.height} @ {self.original_fps} FPS")
        print(f"⚙️  Processing at: {PROCESSING_FPS} FPS")

        # Calculate frame skip
        self.frame_skip = max(1, self.original_fps // PROCESSING_FPS)

    def register_stream(self):
        """Register stream in database"""
        db = SessionLocal()
        try:
            # Check if stream exists
            stream = db.query(StreamInfo).filter(StreamInfo.stream_id == self.stream_id).first()

            if stream:
                # Update existing stream
                stream.status = "active"
                stream.started_at = datetime.utcnow()
            else:
                # Create new stream
                stream = StreamInfo(
                    stream_id=self.stream_id,
                    video_source=str(self.video_source),
                    status="active"
                )
                db.add(stream)

            db.commit()
            print(f"✅ Stream registered in database: {self.stream_id}")
        finally:
            db.close()

    def start(self):
        """
        Start ingesting video frames
        """
        print(f"\n🚀 Starting ingestion for stream: {self.stream_id}")
        print(f"📤 Pushing frames to queue: {FRAME_QUEUE}")
        print("Press Ctrl+C to stop\n")

        frame_count = 0
        processed_count = 0
        start_time = time.time()

        try:
            while self.cap.isOpened():
                ret, frame = self.cap.read()

                if not ret:
                    print("📹 End of video")
                    break

                # Skip frames to match target FPS
                if frame_count % self.frame_skip != 0:
                    frame_count += 1
                    continue

                # Resize frame if needed
                if FRAME_RESIZE_WIDTH and FRAME_RESIZE_WIDTH < self.width:
                    aspect_ratio = self.height / self.width
                    new_height = int(FRAME_RESIZE_WIDTH * aspect_ratio)
                    frame = cv2.resize(frame, (FRAME_RESIZE_WIDTH, new_height))

                # Create message
                timestamp = time.time()
                message = create_frame_message(
                    stream_id=self.stream_id,
                    frame=frame,
                    frame_number=processed_count,
                    timestamp=timestamp,
                    quality=FRAME_QUALITY
                )

                # Push to queue
                self.redis_client.lpush(FRAME_QUEUE, message)
                processed_count += 1

                # Print stats every 30 frames
                if processed_count % 30 == 0:
                    elapsed = time.time() - start_time
                    actual_fps = processed_count / elapsed if elapsed > 0 else 0
                    queue_size = self.redis_client.llen(FRAME_QUEUE)
                    print(f"📊 Frames: {processed_count} | "
                          f"FPS: {actual_fps:.1f} | "
                          f"Queue: {queue_size}")

                frame_count += 1

                # Small sleep to control rate
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\n⏸️  Ingestion stopped by user")
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        self.cap.release()
        print("✅ Ingestion service stopped")


if __name__ == "__main__":
    # Test with webcam
    ingestion = VideoIngestion(
        stream_id="webcam_1",
        video_source=0  # Use your webcam
    )
    ingestion.start()