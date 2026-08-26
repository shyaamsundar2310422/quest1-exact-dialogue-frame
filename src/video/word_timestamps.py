import whisper

MODEL_PATH = "models/tiny.en.pt"
AUDIO_PATH = "data/input/asr_test.wav"

model = whisper.load_model(MODEL_PATH)

result = model.transcribe(
    AUDIO_PATH,
    language="en",
    word_timestamps=True
)

for segment in result["segments"]:
    print(
        f"\nSEGMENT "
        f"{segment['start']:.3f} -> {segment['end']:.3f}"
    )
    print(segment["text"].strip())

    for word in segment.get("words", []):
        print(
            f"  {word['start']:.3f} -> "
            f"{word['end']:.3f}: "
            f"{word['word'].strip()}"
        )