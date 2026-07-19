"""
find_camera_index.py
---------------------
Small standalone helper: tries camera indices 0-5 and shows a live
preview of each one so you can identify which index is your laptop's
built-in webcam and which one is Iriun (or any other virtual/USB camera).

Run:
    python find_camera_index.py

For each index that opens successfully, a preview window pops up.
Press any key to move on to the next index. The window title tells you
the index number. Note down which index shows your phone's camera feed
(that's your IRIUN_INDEX for utils/config.py) and which shows your
laptop's own camera (WEBCAM_INDEX).
"""

import cv2


def main():
    print("Scanning camera indices 0 through 5...")
    print("A preview window will open for each camera that responds.")
    print("Press any key (with the preview window focused) to check the next index.\n")

    found_any = False

    for index in range(6):
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            print(f"Index {index}: not available")
            cap.release()
            continue

        ret, frame = cap.read()
        if not ret or frame is None:
            print(f"Index {index}: opened but no frame received")
            cap.release()
            continue

        found_any = True
        print(f"Index {index}: camera detected — showing preview, press any key to continue")
        cv2.putText(
            frame, f"Camera index: {index}  (press any key)", (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2,
        )
        cv2.imshow(f"Camera Index {index}", frame)
        cv2.waitKey(0)
        cv2.destroyWindow(f"Camera Index {index}")
        cap.release()

    if not found_any:
        print("\nNo cameras were detected on indices 0-5.")
        print("Make sure Iriun Webcam is running on your phone AND the")
        print("Iriun desktop client is running and connected before retrying.")
    else:
        print("\nDone. Update WEBCAM_INDEX / IRIUN_INDEX in utils/config.py")
        print("with the index numbers you identified above.")


if __name__ == "__main__":
    main()
