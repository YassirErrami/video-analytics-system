"""
Configuration for distributed video analytics system
"""

# Redis Configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

# Queue names
FRAME_QUEUE = 'frame_queue'
RESULTS_QUEUE = 'results_queue'

# Video Processing Settings
PROCESSING_FPS = 5  # Process 5 frames per second (lower = faster, fewer detections)
FRAME_RESIZE_WIDTH = 640  # Resize frames to this width for faster processing
FRAME_QUALITY = 85  # JPEG quality (0-100)

# YOLO Model Settings
YOLO_MODEL = 'yolov8n.pt'  # nano model (fastest)
CONFIDENCE_THRESHOLD = 0.5  # Only keep detections above this confidence

# Worker Settings
WORKER_TIMEOUT = 1  # Seconds to wait for new frames before checking again

# Debug Settings
DEBUG = True  # Print debug messages
SHOW_PREVIEW = False  # Don't show video window in distributed mode