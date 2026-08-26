import cv2


def timestamp_to_frame(video_path, timestamp):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_number = round(timestamp * fps)

    if frame_number >= total_frames:
        frame_number = total_frames - 1

    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    success, frame = cap.read()

    if not success:
        cap.release()
        raise RuntimeError(
            f"Unable to read frame {frame_number}"
        )

    actual_timestamp = frame_number / fps

    cap.release()

    return {
        "frame_number": frame_number,
        "timestamp": actual_timestamp,
        "fps": fps,
        "total_frames": total_frames,
        "frame": frame,
    }


def save_frame(video_path, timestamp, output_path):
    result = timestamp_to_frame(video_path, timestamp)

    success = cv2.imwrite(
        output_path,
        result["frame"]
    )

    if not success:
        raise RuntimeError(
            f"Unable to save frame: {output_path}"
        )

    return {
        key: value
        for key, value in result.items()
        if key != "frame"
    }