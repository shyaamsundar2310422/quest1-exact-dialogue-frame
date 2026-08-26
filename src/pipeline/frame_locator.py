import argparse
import json
import os

from src.search.frame_locator import save_frame


def main():
    parser = argparse.ArgumentParser(
        description="Convert a video timestamp to a frame."
    )

    parser.add_argument(
        "--video",
        required=True,
        help="Path to video file."
    )

    parser.add_argument(
        "--timestamp",
        type=float,
        required=True,
        help="Timestamp in seconds."
    )

    parser.add_argument(
        "--output",
        default="data/output/exact_frame.jpg",
        help="Output frame path."
    )

    args = parser.parse_args()

    os.makedirs(
        os.path.dirname(args.output),
        exist_ok=True
    )

    result = save_frame(
        args.video,
        args.timestamp,
        args.output
    )

    print("\nFrame located")
    print("--------------------")
    print(f"Timestamp requested: {args.timestamp:.3f}s")
    print(f"Frame number:        {result['frame_number']}")
    print(f"Actual timestamp:    {result['timestamp']:.3f}s")
    print(f"FPS:                 {result['fps']:.6f}")
    print(f"Total frames:        {result['total_frames']}")
    print(f"Saved:               {args.output}")

    metadata_path = os.path.splitext(
        args.output
    )[0] + ".json"

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(result, f, indent=2)

    print(f"Metadata:             {metadata_path}")


if __name__ == "__main__":
    main()