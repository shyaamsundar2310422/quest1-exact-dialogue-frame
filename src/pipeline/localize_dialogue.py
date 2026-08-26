import argparse
import json
import os
import subprocess

import cv2
import whisper

from src.matching.text_matcher import find_dialogue
from src.search.fine_search import refine_speech_onset

from src.confidence.scorer import calculate_confidence
def extract_audio(video_path, audio_path):
    os.makedirs(
        os.path.dirname(audio_path),
        exist_ok=True
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        audio_path,
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def transcribe(audio_path, model_path):
    print("Loading Whisper model...")

    model = whisper.load_model(model_path)

    print("Transcribing audio...")

    result = model.transcribe(
        audio_path,
        language="en",
        word_timestamps=True,
    )

    return result


def extract_frame(video_path, timestamp, output_path):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(
            f"Unable to open video: {video_path}"
        )

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    frame_number = round(timestamp * fps)

    frame_number = max(
        0,
        min(frame_number, frame_count - 1)
    )

    cap.set(
        cv2.CAP_PROP_POS_FRAMES,
        frame_number
    )

    success, frame = cap.read()

    cap.release()

    if not success:
        raise RuntimeError(
            f"Unable to extract frame {frame_number}"
        )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    cv2.imwrite(output_path, frame)

    return frame_number, fps


def main():
    parser = argparse.ArgumentParser(
        description="Locate an exact video frame for dialogue."
    )

    parser.add_argument(
        "--video",
        required=True
    )

    parser.add_argument(
        "--target",
        required=True
    )

    parser.add_argument(
        "--model",
        default="models/tiny.en.pt"
    )

    parser.add_argument(
        "--output-dir",
        default="data/output"
    )

    args = parser.parse_args()

    audio_path = os.path.join(
        args.output_dir,
        "pipeline_audio.wav"
    )

    frame_path = os.path.join(
        args.output_dir,
        "exact_dialogue_frame.jpg"
    )

    result_path = os.path.join(
        args.output_dir,
        "localization_result.json"
    )

    # ---------------------------------------------------------
    # 1. Extract audio
    # ---------------------------------------------------------

    print("\n[1/5] Extracting audio...")

    extract_audio(
        args.video,
        audio_path
    )

    # ---------------------------------------------------------
    # 2. Whisper transcription
    # ---------------------------------------------------------

    print("\n[2/5] Running transcription...")

    result = transcribe(
        audio_path,
        args.model
    )

    # ---------------------------------------------------------
    # 3. Dialogue matching
    # ---------------------------------------------------------

    print("\n[3/5] Matching target dialogue...")

    match = find_dialogue(
        result,
        args.target
    )

    if match is None:
        raise RuntimeError(
            "Target dialogue was not found."
        )

    print(
        f"Matched text: {match['text']}"
    )

    print(
        f"Match score: {match['score']:.2f}"
    )

    
    words = match.get("words", [])
    if words:
    	candidate_time = words[0].get("start")
    else:
    	candidate_time = match.get("segment_start")

    if candidate_time is None:
    	raise RuntimeError(
        	"Matched dialogue does not contain a usable 	timestamp."
    	)

    print(
        f"Candidate timestamp: {candidate_time:.3f}s"
    )

    # ---------------------------------------------------------
    # 4. Fine temporal refinement
    # ---------------------------------------------------------

    print("\n[4/5] Refining timestamp...")

    refined_time = refine_speech_onset(
        audio_path,
        candidate_time
    )

    print(
        f"Refined timestamp: {refined_time:.3f}s"
    )

    # ---------------------------------------------------------
    # 5. Extract exact frame
    # ---------------------------------------------------------

    print("\n[5/5] Extracting exact frame...")

    frame_number, fps = extract_frame(
        args.video,
        refined_time,
        frame_path
    )
    confidence = calculate_confidence(
    	match["score"],
    	candidate_time,
    	refined_time
    )

    print(
    	f"Confidence: {confidence:.2f}%"
	)

    result_data = {
        "target": args.target,
        "matched_text": match["text"],
        "match_score": match["score"],
        "candidate_timestamp": candidate_time,
        "refined_timestamp": refined_time,
        "frame_number": frame_number,
        "frame_timestamp": frame_number / fps,
        "fps": fps,
        "frame_path": frame_path,
        "confidence": confidence,
    }

    with open(
        result_path,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            result_data,
            f,
            indent=2
        )

    print("\nLocalization complete.")
    print(
        json.dumps(
            result_data,
            indent=2
        )
    )


if __name__ == "__main__":
    main()