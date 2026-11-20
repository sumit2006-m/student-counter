
import cv2
import threading
import time

from flask import Flask, render_template, Response, jsonify
from ultralytics import YOLO

app = Flask(__name__)

# Load AI model
model = YOLO("yolo26n.pt")

# Shared camera data
latest_frame = None
latest_count = 0
camera_status = "Connecting"
lock = threading.Lock()


def camera_loop():
    global latest_frame, latest_count, camera_status

    cap = None

    try:
        while True:
            if cap is None:
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

                if not cap.isOpened():
                    if camera_status != "Disconnected":
                        print("Camera 0 could not be opened with DirectShow.")
                    camera_status = "Disconnected"
                    cap.release()
                    cap = None
                    time.sleep(1)
                    continue

            success, frame = cap.read()

            if not success:
                if camera_status != "Disconnected":
                    print("Camera opened but did not provide a frame; retrying.")
                camera_status = "Disconnected"
                with lock:
                    latest_frame = None
                    latest_count = 0
                cap.release()
                cap = None
                time.sleep(1)
                continue

            if camera_status != "Connected":
                print("Camera connected using DirectShow.")
            camera_status = "Connected"

            # Run YOLO tracking
            results = model.track(
                frame,
                persist=True,
                classes=[0],
                conf=0.65,
                iou=0.5,
                tracker="bytetrack.yaml",
                verbose=False
            )

            result = results[0]

            # Count currently detected people
            count = len(result.boxes)

            # Draw tracking boxes with confidence scores
            output = result.plot(
                labels=True,
                conf=True
            )

            # Add count to video
            cv2.putText(
                output,
                f"People Present: {count}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            # Convert frame into JPEG
            success, buffer = cv2.imencode(".jpg", output)

            if success:
                with lock:
                    latest_frame = buffer.tobytes()
                    latest_count = count
    finally:
        if cap is not None:
            cap.release()


def generate_frames():
    while True:
        with lock:
            frame = latest_frame

        if frame is None:
            time.sleep(0.05)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" +
            frame +
            b"\r\n"
        )


# Main dashboard page
@app.route("/")
def home():
    return render_template("index.html")


# Live camera feed
@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# Live count API
@app.route("/count")
def get_count():
    with lock:
        return jsonify({
            "count": latest_count,
            "status": camera_status,
            "frame_ready": latest_frame is not None
        })


if __name__ == "__main__":

    # Start camera in background thread
    threading.Thread(
        target=camera_loop,
        daemon=True
    ).start()

    # Start Flask server
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
        threaded=True
    )
