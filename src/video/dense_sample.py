import os
import cv2


VIDEO_PATH = "data/input/quest1_video.mp4"
OUTPUT_DIR = "data/samples/dense_305_320"

START_TIME = 305.0
END_TIME = 320.0
INTERVAL = 0.1


def extract_dense_samples():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video: {VIDEO_PATH}")

    current_time = START_TIME

    while current_time <= END_TIME:
        cap.set(cv2.CAP_PROP_POS_MSEC, current_time * 1000)

        success, frame = cap.read()

        if success:
            filename = f"frame_{current_time:.1f}.jpg"
            output_path = os.path.join(OUTPUT_DIR, filename)

            cv2.imwrite(output_path, frame)

            print(f"Saved {filename}")

        current_time += INTERVAL

    cap.release()


if __name__ == "__main__":
    extract_dense_samples()