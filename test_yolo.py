from ultralytics import YOLO
import cv2
import numpy as np

# Download and load YOLOv8 nano model (smallest/fastest)
print("Loading YOLO model...")
model = YOLO('yolov8n.pt')  # This will auto-download first time (~6MB)

# If you have M1/M2/M3 Mac, use Metal acceleration
# model.to('mps')  # Uncomment this line if you have Apple Silicon

print("Model loaded successfully!")
print(f"Model can detect these classes: {model.names}")
#pluss