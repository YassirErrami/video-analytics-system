"""
Utility functions for video analytics system
"""

import cv2
import numpy as np
import base64
import json
from typing import Dict, Any, List


def encode_frame(frame: np.ndarray, quality: int = 85) -> str:
    """
    Encode a video frame to base64 string

    Args:
        frame: OpenCV frame (numpy array)
        quality: JPEG quality (0-100)

    Returns:
        Base64 encoded string
    """
    # Encode frame as JPEG
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, buffer = cv2.imencode('.jpg', frame, encode_param)

    # Convert to base64
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    return frame_base64


def decode_frame(frame_base64: str) -> np.ndarray:
    """
    Decode base64 string back to OpenCV frame

    Args:
        frame_base64: Base64 encoded frame

    Returns:
        OpenCV frame (numpy array)
    """
    # Decode base64
    frame_bytes = base64.b64decode(frame_base64)

    # Convert to numpy array
    nparr = np.frombuffer(frame_bytes, np.uint8)

    # Decode to image
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return frame


def create_frame_message(stream_id: str, frame: np.ndarray,
                         frame_number: int, timestamp: float,
                         quality: int = 85) -> str:
    """
    Create a message to send to the frame queue

    Args:
        stream_id: Unique identifier for the video stream
        frame: OpenCV frame
        frame_number: Frame number in the video
        timestamp: Unix timestamp
        quality: JPEG quality

    Returns:
        JSON string ready to push to queue
    """
    message = {
        'stream_id': stream_id,
        'frame_data': encode_frame(frame, quality),
        'frame_number': frame_number,
        'timestamp': timestamp
    }
    return json.dumps(message)


def parse_frame_message(message_json: str) -> Dict[str, Any]:
    """
    Parse a frame message from the queue

    Returns:
        Dictionary with stream_id, frame, frame_number, timestamp
    """
    message = json.loads(message_json)

    # Decode frame
    frame = decode_frame(message['frame_data'])

    return {
        'stream_id': message['stream_id'],
        'frame': frame,
        'frame_number': message['frame_number'],
        'timestamp': message['timestamp']
    }


def create_result_message(stream_id: str, frame_number: int,
                          timestamp: float, detections: List[Dict]) -> str:
    """
    Create a result message with detection data

    Args:
        stream_id: Stream identifier
        frame_number: Frame number
        timestamp: When frame was captured
        detections: List of detected objects

    Returns:
        JSON string
    """
    message = {
        'stream_id': stream_id,
        'frame_number': frame_number,
        'timestamp': timestamp,
        'detections': detections,
        'num_detections': len(detections)
    }
    return json.dumps(message)


def parse_detections(results, model) -> List[Dict[str, Any]]:
    """
    Parse YOLO results into a clean list of detections

    Args:
        results: YOLO results object
        model: YOLO model (for class names)

    Returns:
        List of detection dictionaries
    """
    detections = []

    if len(results[0].boxes) == 0:
        return detections

    for box in results[0].boxes:
        detection = {
            'class_id': int(box.cls[0]),
            'class_name': model.names[int(box.cls[0])],
            'confidence': float(box.conf[0]),
            'bbox': box.xyxy[0].tolist()  # [x1, y1, x2, y2]
        }
        detections.append(detection)

    return detections