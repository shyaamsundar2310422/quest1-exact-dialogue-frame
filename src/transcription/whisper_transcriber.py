import whisper


class WhisperTranscriber:
    def __init__(self, model_path="models/tiny.en.pt"):
        self.model = whisper.load_model(model_path)

    def transcribe(self, audio_path):
        return self.model.transcribe(
            audio_path,
            language="en",
            task="transcribe",
            word_timestamps=True
        )