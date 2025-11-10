from ultralytics import YOLO
import cv2
import time


def process_video(video_source=0, output_path='output.mp4'):
    """
    Process video and detect objects

    Args:
        video_source: 0 for webcam, or path to video file
        output_path: where to save annotated video
    """

    # Load model
    print("Loading YOLO model...")
    model = YOLO('yolov8n.pt')

    # Uncomment for M1/M2/M3 Macs
    # model.to('mps')

    # Open video source
    print(f"Opening video source: {video_source}")
    cap = cv2.VideoCapture(video_source)

    if not cap.isOpened():
        print("Error: Could not open video source")
        return

    # Get video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Video properties: {width}x{height} @ {fps} FPS")

    # Setup video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    frame_count = 0
    total_time = 0

    print("Processing video... Press 'q' to quit")
    print("=" * 50)

    try:
        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                print("End of video or error reading frame")
                break

            # Run detection
            start_time = time.time()
            results = model(frame, verbose=False)
            inference_time = time.time() - start_time

            # Get annotated frame (with bounding boxes drawn)
            annotated_frame = results[0].plot()

            # Extract detection info
            detections = results[0].boxes
            num_detections = len(detections)

            # Add stats to frame
            stats_text = f"Frame: {frame_count} | Objects: {num_detections} | FPS: {1 / inference_time:.1f}"
            cv2.putText(annotated_frame, stats_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Show detection details
            if num_detections > 0:
                detected_objects = {}
                for box in detections:
                    class_id = int(box.cls[0])
                    class_name = model.names[class_id]
                    confidence = float(box.conf[0])
                    detected_objects[class_name] = detected_objects.get(class_name, 0) + 1

                if frame_count % 30 == 0:  # Print every 30 frames
                    print(f"Frame {frame_count}: {detected_objects}")

            # Write frame
            out.write(annotated_frame)

            # Display (comment out if running headless)
            cv2.imshow('Video Analytics', annotated_frame)

            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nUser requested quit")
                break

            frame_count += 1
            total_time += inference_time

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    finally:
        # Cleanup
        cap.release()
        out.release()
        cv2.destroyAllWindows()

        # Print summary
        avg_fps = frame_count / total_time if total_time > 0 else 0
        print(f"\n{'=' * 50}")
        print(f"SUMMARY")
        print(f"{'=' * 50}")
        print(f"Processed {frame_count} frames")
        print(f"Average FPS: {avg_fps:.2f}")
        print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    # Use webcam
    print("Starting with WEBCAM (source=0)")
    print("A window will open showing live detection")
    print("Press 'q' in the video window to stop")
    print()

    process_video(video_source=0, output_path='webcam_output.mp4')
