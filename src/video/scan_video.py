import os
import cv2


def scan_video(video_path, output_dir, interval=10):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps

    current_time = 0.0

    while current_time <= duration:
        cap.set(cv2.CAP_PROP_POS_MSEC, current_time * 1000)

        success, frame = cap.read()

        if success:
            filename = f"scan_{current_time:07.1f}.jpg"
            output_path = os.path.join(output_dir, filename)

            cv2.imwrite(output_path, frame)

            print(f"Saved: {output_path}")

        current_time += interval

    cap.release()


if __name__ == "__main__":
    scan_video(
        "data/input/quest1_video.mp4",
        "data/samples/full_scan",
        interval=10
    )