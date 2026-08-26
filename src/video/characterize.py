import sys
import cv2


def characterize_video(video_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    duration = frame_count / fps if fps > 0 else 0

    codec_value = int(cap.get(cv2.CAP_PROP_FOURCC))
    codec = "".join(
        chr((codec_value >> (8 * i)) & 0xFF)
        for i in range(4)
    )

    cap.release()

    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration_seconds": duration,
        "width": width,
        "height": height,
        "codec": codec,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.video.characterize <video_path>")
        sys.exit(1)

    result = characterize_video(sys.argv[1])

    print("\nVideo Characterization")
    print("----------------------")

    for key, value in result.items():
        print(f"{key}: {value}")