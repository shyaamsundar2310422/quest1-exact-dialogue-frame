import os
import cv2


def extract_samples(video_path, output_dir, start_time, end_time, interval):
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)

    current_time = start_time

    while current_time <= end_time:
        cap.set(cv2.CAP_PROP_POS_MSEC, current_time * 1000)

        success, frame = cap.read()

        if success:
            filename = f"frame_{current_time:.3f}.jpg"
            output_path = os.path.join(output_dir, filename)

            cv2.imwrite(output_path, frame)

            print(f"Saved: {output_path}")

        current_time += interval

    cap.release()


if __name__ == "__main__":
    video_path = "data/input/quest1_video.mp4"
    output_dir = "data/samples"

    # Research window only.
    # This is NOT part of the final detection algorithm.
    start_time = 305
    end_time = 320
    interval = 0.5

    extract_samples(
        video_path,
        output_dir,
        start_time,
        end_time,
        interval
    )