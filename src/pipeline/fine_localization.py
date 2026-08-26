import argparse
import os

import cv2

from src.search.fine_search import (
    refine_speech_onset,
    timestamp_to_frame,
)


def main():
    parser = argparse.ArgumentParser(
        description="Refine dialogue timestamp and locate frame."
    )

    parser.add_argument(
        "--video",
        required=True
    )

    parser.add_argument(
        "--audio",
        required=True
    )

    parser.add_argument(
        "--timestamp",
        type=float,
        required=True
    )

    parser.add_argument(
        "--output",
        default="data/output/refined_frame.jpg"
    )

    args = parser.parse_args()

    print("Refining speech onset...")

    refined_time = refine_speech_onset(
        args.audio,
        args.timestamp
    )

    print(
        f"Whisper candidate: {args.timestamp:.3f}s"
    )

    print(
        f"Refined onset:     {refined_time:.3f}s"
    )

    frame_number, fps, frame = timestamp_to_frame(
        args.video,
        refined_time
    )

    os.makedirs(
        os.path.dirname(args.output),
        exist_ok=True
    )

    cv2.imwrite(
        args.output,
        frame
    )

    print(f"FPS:                {fps:.6f}")
    print(f"Frame number:       {frame_number}")
    print(f"Frame timestamp:    {frame_number / fps:.3f}s")
    print(f"Saved:              {args.output}")


if __name__ == "__main__":
    main()