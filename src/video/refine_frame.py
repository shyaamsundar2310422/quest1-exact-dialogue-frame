import cv2
import os


VIDEO_PATH = "data/input/quest1_video.mp4"
OUTPUT_DIR = "data/samples/refinement"

TARGET_TIME = 325.280
WINDOW_BEFORE = 0.5
WINDOW_AFTER = 0.5


def refine_frame():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        raise RuntimeError("Unable to open video.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    start_time = TARGET_TIME - WINDOW_BEFORE
    end_time = TARGET_TIME + WINDOW_AFTER

    start_frame = max(0, int(start_time * fps))
    end_frame = min(
        total_frames - 1,
        int(end_time * fps)
    )

    print(f"FPS: {fps}")
    print(f"Candidate time: {TARGET_TIME:.3f}s")
    print(f"Candidate frame: {TARGET_TIME * fps:.2f}")
    print(f"Inspecting frames: {start_frame} -> {end_frame}")

    for frame_number in range(start_frame, end_frame + 1):

        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        success, frame = cap.read()

        if not success:
            continue

        actual_time = frame_number / fps

        filename = (
            f"frame_{frame_number:06d}"
            f"_t_{actual_time:.3f}.jpg"
        )

        output_path = os.path.join(
            OUTPUT_DIR,
            filename
        )

        cv2.imwrite(output_path, frame)

        print(
            f"Saved frame {frame_number} "
            f"at {actual_time:.3f}s"
        )

    cap.release()


if __name__ == "__main__":
    refine_frame()