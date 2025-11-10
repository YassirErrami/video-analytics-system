"""
Results Monitor
Watches the results queue and displays detections in real-time
"""

import redis
import json
import time
from config import *


def monitor_results():
    """Monitor and display results from the queue"""

    # Connect to Redis
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        decode_responses=True
    )

    print("🔍 Results Monitor Started")
    print(f"👂 Listening to: {RESULTS_QUEUE}")
    print("Press Ctrl+C to stop\n")

    total_frames = 0
    total_detections = 0
    start_time = time.time()

    try:
        while True:
            # Pull result from queue
            result = r.brpop(RESULTS_QUEUE, timeout=1)

            if result is None:
                continue

            # Parse result
            _, message_json = result
            data = json.loads(message_json)

            stream_id = data['stream_id']
            frame_number = data['frame_number']
            detections = data['detections']
            num_detections = data['num_detections']

            total_frames += 1
            total_detections += num_detections

            # Print detection summary
            if num_detections > 0:
                detected_objects = {}
                for det in detections:
                    cls = det['class_name']
                    detected_objects[cls] = detected_objects.get(cls, 0) + 1

                print(f"📺 Stream: {stream_id} | "
                      f"Frame: {frame_number} | "
                      f"Objects: {detected_objects}")

            # Print stats every 30 frames
            if total_frames % 30 == 0:
                elapsed = time.time() - start_time
                fps = total_frames / elapsed if elapsed > 0 else 0
                avg_detections = total_detections / total_frames if total_frames > 0 else 0

                print(f"\n📊 Stats: {total_frames} frames | "
                      f"{fps:.1f} FPS | "
                      f"{avg_detections:.1f} avg objects/frame\n")

    except KeyboardInterrupt:
        print("\n⏸️  Monitor stopped")

        # Final stats
        elapsed = time.time() - start_time
        print(f"\n{'=' * 50}")
        print(f"Final Statistics")
        print(f"{'=' * 50}")
        print(f"Total frames: {total_frames}")
        print(f"Total detections: {total_detections}")
        print(f"Time: {elapsed:.2f}s")
        print(f"Average FPS: {total_frames / elapsed if elapsed > 0 else 0:.2f}")
        print(f"{'=' * 50}\n")


if __name__ == "__main__":
    monitor_results()