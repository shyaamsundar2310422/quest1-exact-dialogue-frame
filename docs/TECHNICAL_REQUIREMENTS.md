
# Technical Requirements

## 1. Overview

This document defines the technical requirements for the Quest1 Exact Dialogue Frame Detection system.

The system accepts a video and a target dialogue and determines the corresponding video frame through speech transcription, text matching, temporal refinement, and frame extraction.

---

## 2. System Requirements

### 2.1 Operating Environment

The system is designed to run locally on a development machine.

Recommended environment:

- Windows, Linux, or macOS
- Python 3.x
- Sufficient local storage for video and intermediate audio
- CPU capable of running Whisper inference

GPU acceleration is optional and is not required by the current implementation.

---

## 3. Software Dependencies

The primary Python dependencies are:

| Component | Technology | Purpose |
|---|---|---|
| Programming Language | Python | Application implementation |
| Video Processing | OpenCV | Video metadata and frame extraction |
| Audio Processing | FFmpeg | Audio extraction |
| Speech Recognition | Whisper | Speech-to-text transcription |
| Text Matching | RapidFuzz | Fuzzy dialogue matching |
| OCR | EasyOCR | OCR capability available in the project |
| Video Acquisition | yt-dlp | Video acquisition support |
| User Interface | Streamlit | Interactive application interface |
| Testing | pytest | Automated testing |

FFmpeg must also be available as an executable in the system environment.

---

## 4. Input Requirements

### 4.1 Video Input

The system shall accept a video file as input.

Supported formats include:

```text
MP4
MKV
AVI
MOV
````

The input video must contain an accessible audio track for the primary ASR-based localization workflow.

The Streamlit interface is configured to support uploads of up to approximately:

```text
1 GB
```

---

### 4.2 Target Dialogue

The system shall accept a natural-language dialogue string.

Example:

```text
My mind rebels at stagnation.
```

The target dialogue is used as the search query against the generated transcription.

---

## 5. Video Processing Requirements

The system shall obtain the following video properties when required:

* Frame rate (FPS)
* Frame count
* Video resolution
* Video duration
* Video codec

These properties are used for video characterization and frame-level localization.

---

## 6. Audio Processing Requirements

The system shall extract the audio stream from the input video.

The extracted audio shall be normalized to:

```text
Format: WAV
Channels: Mono
Sample Rate: 16000 Hz
```

FFmpeg shall be used for audio extraction.

The audio extraction process shall fail clearly if the input video cannot be processed.

---

## 7. Speech Recognition Requirements

The system shall perform automatic speech recognition on the extracted audio.

The current implementation uses:

```text
Whisper tiny.en
```

The transcription process shall support:

* English language transcription
* Segment-level timestamps
* Word-level timestamps

Word-level timestamps are required to improve the temporal localization of the target dialogue.

---

## 8. Whisper Model Management

The Whisper model shall be loaded locally.

The model file is treated as a runtime dependency and is excluded from Git version control because of its size.

The Streamlit implementation shall cache the loaded Whisper model using Streamlit resource caching to avoid unnecessary repeated model loading.

Example:

```python
@st.cache_resource
def load_whisper_model(model_path):
    return whisper.load_model(model_path)
```

The first application execution may require model loading time. Subsequent Streamlit interactions can reuse the cached model within the running application process.

---

## 9. Dialogue Matching Requirements

The system shall compare the target dialogue against the generated transcription.

The matching component shall:

1. Normalize the target dialogue.
2. Normalize transcription text.
3. Compare candidate transcript segments.
4. Calculate a similarity score.
5. Select the best matching candidate.

RapidFuzz shall be used for fuzzy similarity matching.

The matching process shall tolerate reasonable differences in:

* Capitalization
* Whitespace
* Punctuation
* Minor transcription variations

---

## 10. Candidate Timestamp Requirements

The system shall obtain a candidate timestamp from the best dialogue match.

Priority shall be given to word-level timestamps.

The selection logic shall be:

```text
Word timestamps available
        ↓
Use first matched word start time

Word timestamps unavailable
        ↓
Use matched segment start time
```

If no usable timestamp is available, the system shall report an error instead of attempting frame extraction with an invalid timestamp.

---

## 11. Temporal Refinement Requirements

The system shall perform an additional refinement step around the candidate timestamp.

The refinement stage shall use the local audio region to estimate the speech onset more precisely.

The output shall be:

```text
Candidate timestamp
        ↓
Refinement
        ↓
Refined timestamp
```

The refined timestamp shall be used for final frame localization.

---

## 12. Frame Localization Requirements

The system shall map the refined timestamp to a video frame.

The frame number shall be calculated using the video's FPS:

```text
frame_number = round(timestamp × FPS)
```

The calculated frame number shall be constrained to the valid range:

```text
0 ≤ frame_number < frame_count
```

This prevents invalid frame access.

---

## 13. Frame Extraction Requirements

OpenCV shall be used to extract the localized frame.

The system shall:

1. Open the video.
2. Obtain FPS and frame count.
3. Calculate the target frame number.
4. Seek to the frame.
5. Read the frame.
6. Save the frame as an image.

The system shall report an error if the video cannot be opened or the target frame cannot be read.

---

## 14. Confidence Requirements

The system shall provide a confidence score for the localization result.

The current confidence calculation uses information from:

* Dialogue match quality
* Candidate timestamp
* Refined timestamp

The confidence score is intended as a practical reliability indicator.

It shall not be interpreted as a statistically calibrated probability.

---

## 15. Output Requirements

The system shall generate structured localization information containing:

```text
Target dialogue
Matched dialogue
Match score
Candidate timestamp
Refined timestamp
Frame number
Frame timestamp
FPS
Confidence score
```

The result shall be available as JSON.

Example:

```json
{
    "target": "My mind rebels at stagnation.",
    "matched_text": "My mind rebels at stagnation.",
    "match_score": 100.0,
    "candidate_timestamp": 325.1,
    "refined_timestamp": 325.25,
    "frame_number": 7798,
    "frame_timestamp": 325.241,
    "fps": 23.976,
    "confidence": 100.0
}
```

The corresponding frame shall also be saved as an image.

---

## 16. User Interface Requirements

The Streamlit interface shall provide:

### Input

* Video upload control
* Target dialogue input
* Localization button

### Processing Feedback

The interface shall display processing stages including:

```text
Extracting audio...
Transcribing audio...
Searching for target dialogue...
Refining dialogue timestamp...
Extracting corresponding frame...
```

### Results

The interface shall display:

* Matched dialogue
* Match score
* Refined timestamp
* Confidence score
* Frame number
* Frame timestamp
* Extracted frame

The user shall also be able to download the structured JSON result.

---

## 17. Command-Line Requirements

The core localization pipeline shall be executable without the Streamlit interface.

The CLI shall support parameters for:

```text
--video
--target
--model
--output-dir
```

Example:

```bash
python -m src.pipeline.localize_dialogue ^
    --video data/input/query_video.mp4 ^
    --target "My mind rebels at stagnation." ^
    --model models/tiny.en.pt ^
    --output-dir data/output
```

---

## 18. Error Handling Requirements

The system shall handle common failure conditions.

### Missing Video

The application shall report that a video is required.

### Missing Dialogue

The application shall report that a target dialogue is required.

### Missing Whisper Model

The application shall report the expected model path.

### Invalid Video

The system shall report an error if the video cannot be opened.

### Audio Extraction Failure

The system shall stop processing if FFmpeg cannot extract the required audio.

### Dialogue Not Found

The system shall report that the target dialogue could not be located.

It shall not return an arbitrary frame.

### Missing Timestamp

The system shall report an error if the matched dialogue does not contain usable timing information.

### Frame Extraction Failure

The system shall report an error if the required frame cannot be extracted.

---

## 19. Performance Requirements

The current system is designed primarily for correctness and reproducibility rather than real-time processing.

Processing time depends on:

* Video duration
* Audio duration
* Whisper model
* CPU/GPU availability
* Video resolution
* Storage performance

For the reference video, complete processing currently requires approximately 10 minutes on the development machine using local CPU-based Whisper inference.

The primary performance bottleneck is speech transcription.

The Whisper model is cached in the Streamlit application to reduce repeated model-loading overhead.

---

## 20. Storage Requirements

Large runtime artifacts shall not be stored in the Git repository.

The following categories shall be excluded from version control:

* Video files
* Generated audio files
* Generated frames
* Local Whisper models
* Python virtual environments
* Python cache files
* Temporary processing artifacts
* Logs
* ASR test artifacts

The `.gitignore` file shall enforce these exclusions.

---

## 21. Modularity Requirements

The implementation shall separate major processing responsibilities.

The current architecture contains modules for:

```text
Acquisition
Matching
Search
Confidence
OCR
Output
Pipeline
Video Processing
```

The end-to-end pipeline shall coordinate these components without placing all processing logic into a single module.

---

## 22. Testing Requirements

The project shall include automated tests for core functionality.

Tests shall be executable using:

```bash
pytest tests -vv
```

The current test suite includes validation for:

* Text normalization
* Basic video metadata/frame calculations

The latest validation produced:

```text
2 passed
```

End-to-end validation is additionally performed using the reference video and target dialogue.

---

## 23. Reproducibility Requirements

The project shall provide sufficient documentation for another developer to:

1. Clone the repository.
2. Install the required dependencies.
3. Configure FFmpeg.
4. Obtain the required Whisper model.
5. Run the CLI pipeline.
6. Launch the Streamlit interface.
7. Execute the automated tests.

The README and documentation under `docs/` provide the required project information.

---

## 24. Security and Repository Requirements

The public GitHub repository shall not contain:

* API keys
* Passwords
* Access tokens
* Private credentials
* Large local model files
* Large video files
* Local virtual environments

Runtime data and environment-specific files shall remain excluded through `.gitignore`.

---

## 25. Technical Acceptance Criteria

The implementation satisfies the technical requirements when:

1. A valid video can be supplied to the system.
2. A target dialogue can be entered.
3. Audio can be extracted successfully.
4. Whisper can generate a transcription.
5. The target dialogue can be matched.
6. A candidate timestamp can be obtained.
7. The timestamp can be refined.
8. The refined timestamp can be mapped to a valid frame.
9. The corresponding frame can be extracted.
10. Match and confidence information can be generated.
11. Results can be displayed through Streamlit.
12. Results can be exported as JSON.
13. Core automated tests pass.
14. The project can be reproduced from the public repository without committing large runtime artifacts.

---

## 26. Technical Summary

The final technical implementation can be represented as:

```text
                    Video
                      │
                      ▼
                ┌───────────┐
                │  FFmpeg   │
                │   Audio   │
                └─────┬─────┘
                      │
                      ▼
                ┌───────────┐
                │  Whisper  │
                │    ASR    │
                └─────┬─────┘
                      │
                Word Timestamps
                      │
                      ▼
                ┌───────────┐
                │ RapidFuzz │
                │  Matching │
                └─────┬─────┘
                      │
              Candidate Timestamp
                      │
                      ▼
                ┌───────────┐
                │ Temporal  │
                │ Refinement│
                └─────┬─────┘
                      │
                Refined Timestamp
                      │
                      ▼
                ┌───────────┐
                │  OpenCV   │
                │   Frame   │
                └─────┬─────┘
                      │
                      ▼
              Exact Dialogue Frame
                      │
                      ▼
             Confidence + JSON
                      │
             ┌────────┴────────┐
             ▼                 ▼
        Streamlit UI       CLI Output
```

