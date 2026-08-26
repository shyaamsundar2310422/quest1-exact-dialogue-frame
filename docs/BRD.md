
# Business Requirements Document (BRD)

## 1. Project Overview

### Project Name
Quest1 — Exact Dialogue Frame Detection

### Purpose

The objective of this project is to automatically identify the exact video frame in which a specified dialogue first appears.

The system eliminates the need for a user to manually inspect a long video to locate a particular spoken dialogue.

Given a video and a target dialogue, the system processes the video, identifies the occurrence of the dialogue, determines its precise timestamp, and extracts the corresponding video frame.

---

## 2. Problem Statement

Given a video and a target dialogue, the system must automatically identify:

1. The first video frame corresponding to the dialogue.
2. The timestamp of the identified frame.
3. The extracted dialogue text.
4. The frame number, where applicable.
5. The corresponding video frame as an image.

For the provided reference case, the target dialogue is:

> "My mind rebels at stagnation."

The solution should work without requiring manual inspection of the video.

---

## 3. Business Objective

The primary objective is to provide an automated and reproducible method for locating dialogue within video content.

The system should:

- Reduce manual video-search effort.
- Locate dialogue accurately at frame level.
- Provide evidence of the detected location through the extracted frame.
- Provide structured output containing localization metadata.
- Be usable through a simple interface.
- Be sufficiently robust to handle normal variations in video quality, resolution, and frame rate.

---

## 4. Scope

### 4.1 In Scope

The system includes:

- Video input through the application interface.
- Support for commonly used video formats.
- Audio extraction from the input video.
- Automatic speech transcription.
- Dialogue matching against the target text.
- Timestamp identification using word-level speech timestamps.
- Fine temporal refinement of the dialogue onset.
- Conversion of the refined timestamp to a video frame.
- Extraction of the corresponding frame as an image.
- Match scoring and confidence estimation.
- Display of localization results.
- JSON result generation.
- Command-line execution.
- Streamlit-based user interface.

### 4.2 Out of Scope

The current system does not aim to:

- Perform general video understanding.
- Identify every dialogue in a video.
- Generate subtitles for the complete video.
- Perform speaker identification.
- Perform facial recognition.
- Automatically edit or modify the source video.
- Guarantee real-time processing for long videos.

---

## 5. Users

The primary users of the system are:

- Evaluators who need to verify the exact location of a dialogue.
- Developers or researchers working with video analysis.
- Users who need to locate specific spoken content in long videos without manually watching the entire video.

---

## 6. Functional Requirements

### FR-01: Video Input

The system shall accept a video as input.

The application interface shall support common video formats including:

- MP4
- MKV
- AVI
- MOV

The current Streamlit interface supports video uploads up to approximately 1 GB.

---

### FR-02: Target Dialogue Input

The system shall allow the user to enter the dialogue they want to locate.

Example:

```text
My mind rebels at stagnation.
````

---

### FR-03: Audio Extraction

The system shall extract the audio track from the input video before speech processing.

The extracted audio shall be converted to a suitable format for speech recognition.

---

### FR-04: Speech Transcription

The system shall automatically transcribe the extracted audio.

The transcription shall provide timing information at word level where available.

---

### FR-05: Dialogue Matching

The system shall compare the target dialogue against the generated transcription.

The system shall determine the best matching dialogue segment and provide a matching score.

---

### FR-06: Timestamp Localization

The system shall determine a candidate timestamp corresponding to the beginning of the matched dialogue.

Word-level timestamps shall be preferred when available.

---

### FR-07: Temporal Refinement

The system shall refine the candidate timestamp to estimate the actual onset of the spoken dialogue more precisely.

---

### FR-08: Frame Localization

The system shall convert the refined timestamp into a video frame position using the video's frame rate.

---

### FR-09: Frame Extraction

The system shall extract the corresponding video frame as an image.

---

### FR-10: Result Generation

The system shall provide, at minimum:

* Target dialogue
* Matched dialogue text
* Match score
* Candidate timestamp
* Refined timestamp
* Frame number
* Frame timestamp
* Video FPS
* Confidence score
* Extracted frame

---

### FR-11: Uncertain or Failed Matches

If the target dialogue cannot be located with sufficient confidence, the system shall report that the dialogue could not be reliably found instead of returning an arbitrary frame.

---

### FR-12: User Interface

The system shall provide a simple interface through which a user can:

1. Upload a video.
2. Enter the target dialogue.
3. Start processing.
4. View processing progress.
5. View the localization result.
6. View the extracted frame.
7. Download the result as JSON.

---

## 7. Non-Functional Requirements

### NFR-01: Accuracy

The system should identify the dialogue location accurately enough to extract the first relevant video frame.

---

### NFR-02: Robustness

The solution should be reasonably robust to normal variations in:

* Video resolution
* Frame rate
* Video quality
* Audio quality
* Dialogue wording variations

---

### NFR-03: Automation

The solution shall not require the user to manually search through the video to identify the relevant portion.

---

### NFR-04: Reproducibility

Given the same video, target dialogue, and processing configuration, the system should produce a consistent localization result.

---

### NFR-05: Usability

The application should provide clear processing status and understandable output.

---

### NFR-06: Maintainability

The implementation should separate major processing responsibilities such as:

* Audio extraction
* Transcription
* Dialogue matching
* Timestamp refinement
* Frame extraction
* Confidence scoring
* Result presentation

---

### NFR-07: Performance

Processing time may vary depending on video duration, audio length, model configuration, and available hardware.

The current implementation performs local speech transcription and is optimized primarily for correctness and reproducibility rather than real-time processing.

---

## 8. Success Criteria

The project is considered successful when the system can:

1. Accept a video and target dialogue.
2. Process the video automatically.
3. Locate the target dialogue in the generated transcription.
4. Determine a candidate timestamp.
5. Refine the timestamp.
6. Map the refined timestamp to a video frame.
7. Extract the corresponding frame.
8. Return the dialogue text and localization metadata.
9. Display the extracted frame to the user.
10. Provide sufficient information to verify the detected result.

For the reference dialogue:

```text
"My mind rebels at stagnation."
```

the system successfully identifies the dialogue and extracts the corresponding video frame.

---

## 9. Constraints

The current implementation has the following practical constraints:

* Speech transcription is performed locally.
* Processing long videos can require significant CPU time.
* The accuracy of localization depends partly on speech-recognition quality.
* Videos with unclear or heavily distorted audio may reduce transcription accuracy.
* The current system is designed as a prototype rather than a real-time production service.

---

## 10. Future Scope

Potential future improvements include:

* GPU-accelerated transcription.
* Faster or optimized ASR models.
* Audio chunking and parallel processing.
* Transcript caching for repeated searches.
* Support for multiple target dialogues in a single run.
* Improved confidence calibration.
* Additional subtitle-based localization when subtitle tracks are available.
* More advanced visual verification around the detected frame.
* Scalable deployment for larger video collections.

```

