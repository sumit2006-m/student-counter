from ultralytics import YOLO 
import cv2 
model = YOLO("yolo26n.pt")
cap = cv2.VideoCapture(0)
window_name = "Smart people counter"

try:
    if not cap.isOpened():
        raise RuntimeError("Could not open the camera. Check that it is connected and not in use.")

    while True:
        success, frame = cap.read()
        if not success:
            print("Camera not working properly!")
            break

        results = model.track(
            frame,
            persist=True,
            tracker="bytetrack.yaml",
            classes=[0],
            verbose=False,
        )
        result = results[0]
        count = len(result.boxes)
        output = result.plot()
        cv2.putText(
            output,
            f"People present: {count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
        cv2.imshow(window_name, output)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27) or cv2.getWindowProperty(
            window_name, cv2.WND_PROP_VISIBLE
        ) < 1:
            break
finally:
    cap.release()
    cv2.destroyAllWindows()

                