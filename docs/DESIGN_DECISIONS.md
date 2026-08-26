
# Design Decisions

## 1. Overview

This document records the major technical and architectural decisions made during the development of the Quest1 Exact Dialogue Frame Detection system.

The goal was to build a reproducible system that can locate the first video frame corresponding to a specified spoken dialogue.

---

## 2. Speech-Based Localization Instead of Subtitle Dependency

### Decision

Use automatic speech recognition (ASR) as the primary dialogue localization method.

### Reason

The reference video did not provide a reliable subtitle track that could be directly used for localization.

A subtitle-dependent solution would therefore not satisfy the actual input condition.

Speech recognition allows the system to derive dialogue and timing information directly from the video's audio track.

### Result

The pipeline can operate directly from the video and its audio without requiring an external subtitle file.

---

## 3. Whisper for Automatic Speech Recognition

### Decision

Use OpenAI Whisper for speech transcription.

### Reason

Whisper provides:

- Automatic speech recognition
- English transcription
- Segment-level timestamps
- Word-level timestamps
- Local execution

Word-level timestamps are particularly useful because the project requires localization at frame level rather than simply identifying the approximate scene.

### Result

The system can obtain a candidate timestamp corresponding to the beginning of the matched dialogue.

---

## 4. Tiny English Whisper Model

### Decision

Use the `tiny.en` Whisper model.

### Reason

The reference task uses English dialogue, so an English-specific model is appropriate.

The smaller model provides a practical balance between:

- Transcription capability
- Local resource requirements
- Processing time

A larger model could potentially improve transcription accuracy but would increase computational requirements and processing time.

### Result

The project remains feasible to run locally on a CPU-based development environment.

---

## 5. FFmpeg for Audio Extraction

### Decision

Use FFmpeg to extract audio from the input video.

### Reason

The speech-recognition stage requires an audio input.

FFmpeg provides reliable support for extracting audio from common video formats and allows the extracted audio to be converted into a consistent format.

The implementation converts the audio to:

- Mono audio
- 16 kHz sample rate
- WAV format

### Result

The ASR stage receives a standardized audio input regardless of the original video's audio format.

---

## 6. Fuzzy Text Matching

### Decision

Use RapidFuzz for dialogue matching.

### Reason

Speech recognition output may not always exactly match the target dialogue because of:

- Minor transcription errors
- Punctuation differences
- Capitalization differences
- Extra or missing whitespace
- Small wording variations

The matching component therefore normalizes text and uses fuzzy similarity rather than relying only on exact string equality.

### Result

The system can identify the best matching transcription segment and produce a numerical match score.

---

## 7. Text Normalization Before Matching

### Decision

Normalize both the target dialogue and transcription before similarity comparison.

### Reason

Differences such as:

```text
My mind rebels at stagnation.
````

and:

```text
my mind rebels at stagnation
```

should not be treated as completely different dialogue.

The normalization process:

* Converts text to lowercase
* Removes leading and trailing whitespace
* Normalizes internal whitespace

### Result

The matching process becomes less sensitive to formatting differences.

---

## 8. Word-Level Timestamp Selection

### Decision

Use the first word's timestamp from the best matching dialogue segment when available.

### Reason

Segment-level timestamps may cover a larger portion of speech than the exact beginning of the requested dialogue.

Word-level timestamps provide a more precise starting point.

The system therefore uses:

```text
First matching word timestamp
        ↓
Candidate dialogue onset
```

If word-level timestamps are unavailable, the implementation falls back to the segment start timestamp.

### Result

The system obtains a more precise candidate timestamp for subsequent refinement.

---

## 9. Temporal Refinement Before Frame Extraction

### Decision

Perform a fine temporal refinement step after ASR-based matching.

### Reason

ASR timestamps are useful but are not guaranteed to represent the exact physical onset of speech.

A small timing error can result in extracting the wrong video frame.

Therefore, the candidate timestamp is passed to a local speech-onset refinement stage before converting it to a frame.

### Result

The pipeline becomes:

```text
ASR timestamp
      ↓
Candidate dialogue onset
      ↓
Temporal refinement
      ↓
Refined timestamp
      ↓
Video frame
```

This separates speech recognition from precise temporal localization.

---

## 10. OpenCV for Frame Extraction

### Decision

Use OpenCV for video frame access and extraction.

### Reason

The final localization result must be expressed as an actual video frame.

OpenCV provides access to:

* Video FPS
* Total frame count
* Frame positioning
* Individual frame extraction
* Image writing

The refined timestamp is converted to a frame number using:

```text
frame_number = round(timestamp × FPS)
```

The corresponding frame is then extracted from the video.

### Result

The system produces an actual image representing the detected dialogue frame.

---

## 11. Confidence Scoring

### Decision

Include a confidence score in the final result.

### Reason

Dialogue localization depends on multiple stages, including:

* Text matching
* Candidate timestamp selection
* Timestamp refinement

A single match score does not represent the entire localization process.

A separate confidence score provides an additional indication of how reliable the final localization is.

### Result

The UI and JSON output provide both:

* Match score
* Overall localization confidence

---

## 12. Python Modular Architecture

### Decision

Separate the system into functional Python modules.

### Reason

The project contains several independent processing responsibilities.

Separating them makes the code easier to:

* Understand
* Test
* Debug
* Modify
* Reuse

Major components include:

```text
Acquisition
    ↓
Audio Extraction
    ↓
Transcription
    ↓
Dialogue Matching
    ↓
Temporal Refinement
    ↓
Frame Extraction
    ↓
Confidence Scoring
    ↓
Result Output
```

### Result

The project avoids putting the entire processing pipeline into a single monolithic script.

---

## 13. Command-Line Interface

### Decision

Maintain a command-line entry point for the localization pipeline.

### Reason

The CLI provides a simple way to execute and validate the core pipeline independently of the user interface.

It also makes the processing pipeline easier to test during development.

### Result

The core functionality can be executed without Streamlit.

---

## 14. Streamlit for the User Interface

### Decision

Use Streamlit for the application interface.

### Reason

The project requires a simple way for users to:

1. Upload a video.
2. Enter dialogue.
3. Start processing.
4. Observe progress.
5. View the extracted frame.
6. View localization metrics.
7. Download the result.

Streamlit provides these capabilities without requiring a separate frontend/backend architecture.

### Result

The core Python pipeline is exposed through a lightweight web interface.

---

## 15. Whisper Model Caching in Streamlit

### Decision

Cache the loaded Whisper model using Streamlit's resource caching mechanism.

### Reason

Loading the Whisper model repeatedly introduces unnecessary overhead when the Streamlit application reruns.

The model is therefore loaded through a cached resource:

```python
@st.cache_resource
def load_whisper_model(model_path):
    return whisper.load_model(model_path)
```

### Result

Once loaded, the Whisper model can be reused by subsequent Streamlit interactions within the same application session/process.

This reduces repeated model-loading overhead while preserving the existing transcription pipeline.

---

## 16. Local Processing

### Decision

Perform the major processing stages locally.

### Reason

The project needs to be reproducible without depending on external hosted transcription or video-processing services.

Local processing also keeps the video and audio within the local execution environment.

### Result

The current system uses locally available:

* FFmpeg
* Whisper
* OpenCV
* Python processing modules

---

## 17. Temporary Processing Files

### Decision

Use temporary directories for Streamlit processing.

### Reason

Uploaded videos and intermediate audio files can be large.

Keeping temporary processing data outside the permanent repository prevents generated files from unnecessarily accumulating in the project.

### Result

The Streamlit workflow creates temporary files during processing and removes them when processing is complete.

---

## 18. Generated Data Excluded from Version Control

### Decision

Exclude generated videos, audio files, model files, caches, and other large runtime artifacts from Git tracking.

### Reason

The project repository should contain:

* Source code
* Documentation
* Configuration
* Tests
* Required lightweight project assets

Large generated artifacts should not unnecessarily increase repository size.

The `.gitignore` therefore excludes generated media, local models, environments, caches, and test artifacts.

### Result

The GitHub repository remains focused on the reproducible project implementation rather than local runtime data.

---

## 19. JSON Result Output

### Decision

Provide structured JSON output for localization results.

### Reason

The result contains multiple fields that are useful beyond the visual frame:

* Target dialogue
* Matched text
* Match score
* Candidate timestamp
* Refined timestamp
* Frame number
* Frame timestamp
* FPS
* Confidence

JSON provides a simple machine-readable representation of these values.

### Result

The localization result can be consumed by other tools or inspected independently of the UI.

---

## 20. Error Handling

### Decision

Validate major processing stages and report failures clearly.

### Reason

Potential failures include:

* Missing video
* Missing target dialogue
* Missing Whisper model
* Invalid video
* Failed audio extraction
* Dialogue not found
* Missing timestamp
* Failed frame extraction

The system therefore performs validation and reports processing failures rather than silently producing an incorrect result.

### Result

Users receive meaningful feedback when localization cannot be completed.

---

## 21. Design Summary

The final design prioritizes:

* Accurate dialogue localization
* Frame-level output
* Reproducibility
* Modular implementation
* Local execution
* Simple user interaction
* Clear intermediate processing stages
* Structured output

The resulting architecture is:

```text
                    Input Video
                         │
                         ▼
                  Audio Extraction
                         │
                         ▼
                 Whisper Transcription
                         │
                         ▼
                  Dialogue Matching
                         │
                         ▼
               Candidate Timestamp
                         │
                         ▼
              Temporal Refinement
                         │
                         ▼
                 Exact Frame Mapping
                         │
                         ▼
                  Frame Extraction
                         │
                         ▼
                Confidence Scoring
                         │
                         ▼
             ┌───────────┴───────────┐
             ▼                       ▼
        Streamlit UI             JSON Output
```

This design provides a complete path from raw video input to an independently verifiable exact dialogue frame.

```

