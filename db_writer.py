"""
Database Writer Service
Pulls detection results from Redis and writes to PostgreSQL
"""

import redis
import json
import time
from sqlalchemy.orm import Session
from database import SessionLocal, Detection, StreamInfo
from config import *


class DatabaseWriter:
    def __init__(self):
        """Initialize database writer"""

        # Connect to Redis
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )

        try:
            self.redis_client.ping()
            print("✅ Connected to Redis")
        except redis.ConnectionError:
            print("❌ Could not connect to Redis!")
            raise

        # Test database connection
        try:
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            print("✅ Connected to PostgreSQL")
        except Exception as e:
            print(f"❌ Could not connect to PostgreSQL: {e}")
            raise

        self.writes_count = 0

    def write_result(self, result_data: dict, db: Session):
        """
        Write a detection result to database

        Args:
            result_data: Detection result dictionary
            db: Database session
        """

        # Create detection record
        detection = Detection(
            stream_id=result_data['stream_id'],
            frame_number=result_data['frame_number'],
            timestamp=result_data['timestamp'],
            num_detections=result_data['num_detections'],
            detections=result_data['detections']
        )

        db.add(detection)

        # Update stream info
        stream = db.query(StreamInfo).filter(
            StreamInfo.stream_id == result_data['stream_id']
        ).first()

        if stream:
            stream.frames_processed += 1
            stream.total_detections += result_data['num_detections']

        db.commit()
        self.writes_count += 1

    def start(self):
        """
        Start consuming results from Redis and writing to database
        """
        print(f"\n🚀 Database Writer started")
        print(f"👂 Listening to: {RESULTS_QUEUE}")
        print("Press Ctrl+C to stop\n")

        last_stats_time = time.time()

        try:
            while True:
                # Pull result from queue
                result = self.redis_client.brpop(RESULTS_QUEUE, timeout=1)

                if result is None:
                    if time.time() - last_stats_time > 5:
                        print("⏳ Waiting for results...")
                        last_stats_time = time.time()
                    continue

                # Parse result
                _, message_json = result
                result_data = json.loads(message_json)

                # Write to database
                db = SessionLocal()
                try:
                    self.write_result(result_data, db)

                    # Print stats every 30 writes
                    if self.writes_count % 30 == 0:
                        total_detections = db.query(Detection).count()
                        queue_size = self.redis_client.llen(RESULTS_QUEUE)

                        print(f"📊 Writes: {self.writes_count} | "
                              f"Total in DB: {total_detections} | "
                              f"Queue: {queue_size}")

                finally:
                    db.close()

        except KeyboardInterrupt:
            print("\n⏸️  Database writer stopped")
        except Exception as e:
            print(f"❌ Error: {e}")
            raise


if __name__ == "__main__":
    writer = DatabaseWriter()
    writer.start()