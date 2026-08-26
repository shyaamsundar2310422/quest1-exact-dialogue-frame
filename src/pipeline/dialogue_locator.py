import argparse
import json
import os

from src.transcription.whisper_transcriber import WhisperTranscriber
from src.matching.text_matcher import find_dialogue


def main():
    parser = argparse.ArgumentParser(
        description="Locate dialogue in a video using Whisper."
    )

    parser.add_argument(
        "--audio",
        required=True,
        help="Path to extracted audio WAV file."
    )

    parser.add_argument(
        "--target",
        required=True,
        help="Target dialogue."
    )

    parser.add_argument(
        "--model",
        default="models/tiny.en.pt",
        help="Path to Whisper model."
    )

    args = parser.parse_args()

    if not os.path.exists(args.audio):
        raise FileNotFoundError(args.audio)

    if not os.path.exists(args.model):
        raise FileNotFoundError(args.model)

    print("Loading Whisper model...")

    transcriber = WhisperTranscriber(args.model)

    print("Transcribing audio...")

    result = transcriber.transcribe(args.audio)

    print("Searching for target dialogue...")

    match = find_dialogue(
        result,
        args.target
    )

    if match is None:
        print("Target dialogue not found.")
        return

    print("\nMatch found")
    print("--------------------")
    print(f"Text: {match['text']}")
    print(f"Score: {match['score']:.2f}")
    print(
        f"Segment: "
        f"{match['segment_start']:.3f}s -> "
        f"{match['segment_end']:.3f}s"
    )

    if match["words"]:
        print("\nWord timestamps:")

        for word in match["words"]:
            print(
                f"{word['start']:.3f}s -> "
                f"{word['end']:.3f}s : "
                f"{word['word'].strip()}"
            )

    with open(
        "data/output/dialogue_match.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(match, f, indent=2)

    print("\nSaved: data/output/dialogue_match.json")


if __name__ == "__main__":
    main()
