"""
Detection Worker
Pulls frames from Redis queue, runs YOLO detection, pushes results back
"""

import redis
import time
from ultralytics import YOLO
from config import *
from utils import parse_frame_message, create_result_message, parse_detections
import sys


class DetectionWorker:
    def __init__(self, worker_id: str):
        """
        Initialize a detection worker

        Args:
            worker_id: Unique identifier for this worker
        """
        self.worker_id = worker_id

        # Connect to Redis
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True
        )

        # Test connection
        try:
            self.redis_client.ping()
            print(f"✅ Worker {worker_id}: Connected to Redis")
        except redis.ConnectionError:
            print(f"❌ Worker {worker_id}: Could not connect to Redis!")
            raise

        # Load YOLO model
        print(f"🔄 Worker {worker_id}: Loading YOLO model...")
        self.model = YOLO(YOLO_MODEL)

        # Use MPS (Metal) for M1/M2/M3 Macs
        # Uncomment this line if you have Apple Silicon:
        # self.model.to('mps')

        print(f"✅ Worker {worker_id}: Model loaded")

        self.frames_processed = 0
        self.total_inference_time = 0

    def process_frame(self, frame_data: dict):
        """
        Process a single frame

        Args:
            frame_data: Dictionary with stream_id, frame, frame_number, timestamp
        """
        stream_id = frame_data['stream_id']
        frame = frame_data['frame']
        frame_number = frame_data['frame_number']
        timestamp = frame_data['timestamp']

        # Run detection
        start_time = time.time()
        results = self.model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
        inference_time = time.time() - start_time

        # Parse detections
        detections = parse_detections(results, self.model)

        # Create result message
        result_message = create_result_message(
            stream_id=stream_id,
            frame_number=frame_number,
            timestamp=timestamp,
            detections=detections
        )

        # Push to results queue
        self.redis_client.lpush(RESULTS_QUEUE, result_message)

        # Update stats
        self.frames_processed += 1
        self.total_inference_time += inference_time

        # Print detection info
        if DEBUG and detections:
            detected_classes = {}
            for det in detections:
                cls = det['class_name']
                detected_classes[cls] = detected_classes.get(cls, 0) + 1

            print(f"🔍 Worker {self.worker_id} | "
                  f"Frame {frame_number} | "
                  f"Detected: {detected_classes} | "
                  f"Time: {inference_time:.3f}s")

    def start(self):
        """
        Start processing frames from the queue
        """
        print(f"\n🚀 Worker {self.worker_id} started")
        print(f"👂 Listening to queue: {FRAME_QUEUE}")
        print(f"📤 Sending results to: {RESULTS_QUEUE}")
        print("Press Ctrl+C to stop\n")

        last_stats_time = time.time()

        try:
            while True:
                # Pull frame from queue (blocking with timeout)
                result = self.redis_client.brpop(FRAME_QUEUE, timeout=WORKER_TIMEOUT)

                if result is None:
                    # No frames available, wait a bit
                    if DEBUG and time.time() - last_stats_time > 5:
                        print(f"⏳ Worker {self.worker_id}: Waiting for frames...")
                        last_stats_time = time.time()
                    continue

                # Parse message
                _, message_json = result
                frame_data = parse_frame_message(message_json)

                # Process the frame
                self.process_frame(frame_data)

                # Print stats every 30 frames
                if self.frames_processed % 30 == 0:
                    avg_fps = self.frames_processed / self.total_inference_time if self.total_inference_time > 0 else 0
                    queue_size = self.redis_client.llen(FRAME_QUEUE)
                    results_size = self.redis_client.llen(RESULTS_QUEUE)

                    print(f"📊 Worker {self.worker_id} | "
                          f"Processed: {self.frames_processed} | "
                          f"Avg FPS: {avg_fps:.1f} | "
                          f"Queue: {queue_size} | "
                          f"Results: {results_size}")

        except KeyboardInterrupt:
            print(f"\n⏸️  Worker {self.worker_id} stopped by user")
        except Exception as e:
            print(f"❌ Worker {self.worker_id} error: {e}")
            raise
        finally:
            self.print_summary()

    def print_summary(self):
        """Print worker statistics"""
        avg_fps = self.frames_processed / self.total_inference_time if self.total_inference_time > 0 else 0
        print(f"\n{'=' * 50}")
        print(f"Worker {self.worker_id} Summary")
        print(f"{'=' * 50}")
        print(f"Frames processed: {self.frames_processed}")
        print(f"Total time: {self.total_inference_time:.2f}s")
        print(f"Average FPS: {avg_fps:.2f}")
        print(f"{'=' * 50}\n")


if __name__ == "__main__":
    # Get worker ID from command line or use default
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "worker_1"

    worker = DetectionWorker(worker_id)
    worker.start()