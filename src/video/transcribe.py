from faster_whisper import WhisperModel


AUDIO_PATH = "data/input/quest1_audio.wav"


def transcribe_audio():
    print("Loading Whisper model...")

    model = WhisperModel(
        "tiny",
        device="cpu",
        compute_type="int8"
    )

    print("Starting transcription...")

    segments, info = model.transcribe(
        AUDIO_PATH,
        beam_size=5,
        word_timestamps=True
    )

    print(f"\nDetected language: {info.language}")
    print(f"Language probability: {info.language_probability:.3f}\n")

    for segment in segments:
        print(
            f"[{segment.start:.2f} -> {segment.end:.2f}] "
            f"{segment.text.strip()}"
        )


if __name__ == "__main__":
    transcribe_audio()