
# Technical Stack Decision

## 1. Objective

Identify, evaluate, and validate the technical components required to locate a target dialogue in a video and return the corresponding video frame.

The stack selection was driven by the characteristics of the supplied reference video and the requirement for frame-level localization.

---

## 2. Video Feasibility Findings

### 2.1 Video Characteristics

The reference video was characterized before selecting the final processing approach.

| Property | Observed Value |
|---|---:|
| Container | MP4 |
| Video Codec | H.264 |
| Resolution | 960 × 720 |
| Frame Rate | Approximately 23.976 FPS |
| Duration | Approximately 3192.73 seconds |
| Frame Count | 76,549 |

The video therefore contains sufficient frame-level temporal resolution for precise frame localization.

---

## 3. Audio Feasibility

### 3.1 Audio Characteristics

The video contains an AAC audio stream.

The observed audio duration is approximately:

```text
3192.77 seconds
````

The audio was successfully extracted to WAV format with:

```text
Channels: Mono
Sample Rate: 16 kHz
```

This confirmed that the audio track could be used as an input to an automatic speech-recognition system.

---

## 4. Subtitle Availability

FFprobe was used to inspect the media streams.

The available streams were:

```text
H.264 video stream
AAC audio stream
```

No separate subtitle stream was available.

Therefore, a subtitle-dependent localization approach could not be used as the primary mechanism for the supplied video.

---

## 5. Visual Sampling and OCR Feasibility

A coarse frame-sampling experiment was performed across the video.

The target dialogue was not identified as visible burned-in text in the sampled frames.

Therefore, full-video OCR was not selected as the primary dialogue-localization mechanism.

OCR remains available as an optional component for future visual analysis or fallback scenarios where dialogue-related text is actually visible in the video.

---

## 6. Speech Recognition Feasibility

OpenAI Whisper was evaluated as the primary speech-to-text localization mechanism.

### Target Dialogue

```text
"My mind rebels at stagnation."
```

The dialogue was successfully recognized by Whisper.

The feasibility test produced the following word-level timestamps:

| Word       | Start (s) | End (s) |
| ---------- | --------: | ------: |
| My         |    25.280 |  25.460 |
| mind       |    25.460 |  25.800 |
| rebels     |    25.800 |  26.440 |
| at         |    26.440 |  26.940 |
| stagnation |    26.940 |  27.660 |

The ASR test audio began at approximately 300 seconds in the original video.

Therefore, the approximate original-video onset of the target dialogue from this feasibility experiment was:

```text
300 + 25.280 ≈ 325.280 seconds
```

This established that speech recognition could provide a usable temporal localization signal.

---

## 7. Technology Evaluation

| Component            | Selected Technology         | Reason                                                              |
| -------------------- | --------------------------- | ------------------------------------------------------------------- |
| Programming Language | Python                      | Suitable ecosystem for audio, video, and AI processing              |
| Video Acquisition    | yt-dlp                      | Successfully used to acquire the reference video                    |
| Media Processing     | FFmpeg                      | Successfully used for audio extraction                              |
| Video Processing     | OpenCV                      | Used for video characterization, frame access, and frame extraction |
| Speech Recognition   | OpenAI Whisper              | Successfully recognized the target dialogue                         |
| Word Timestamps      | Whisper word timestamps     | Provides temporal localization at word level                        |
| Text Matching        | RapidFuzz                   | Provides robust matching between target dialogue and ASR output     |
| Temporal Refinement  | Local audio analysis        | Refines the ASR-derived candidate timestamp                         |
| Frame Localization   | OpenCV                      | Provides frame-level access using video FPS                         |
| OCR                  | EasyOCR / optional fallback | Not selected as the primary mechanism for the tested video          |
| User Interface       | Streamlit                   | Provides a lightweight interface over the Python pipeline           |
| Testing              | pytest                      | Provides automated testing of core components                       |

---

## 8. Technology Selection Rationale

### 8.1 Python

Python was selected because the project requires integration across:

* Video processing
* Audio processing
* Speech recognition
* Text matching
* Machine learning
* Testing
* User interface development

Python provides suitable libraries across all of these areas.

---

### 8.2 yt-dlp

`yt-dlp` was selected for video acquisition because it successfully acquired the reference video from the supplied OK.ru source during feasibility testing.

It is used during acquisition rather than being part of the core frame-localization algorithm.

---

### 8.3 FFmpeg

FFmpeg was selected for media processing because it provides reliable extraction and conversion of the video's audio stream.

The implemented pipeline uses FFmpeg to produce a standardized mono 16 kHz WAV file for Whisper.

---

### 8.4 OpenAI Whisper

Whisper was selected because the target information is spoken dialogue and the reference video did not contain a usable subtitle stream.

An important requirement was access to temporal information in addition to transcription.

Whisper provides word-level timestamps, allowing the recognized dialogue to be mapped to a region of the source video.

The current implementation uses the English-specific `tiny.en` model.

---

### 8.5 RapidFuzz

RapidFuzz was selected for dialogue matching because ASR output may differ slightly from the user-provided target dialogue.

Potential differences include:

* Capitalization
* Punctuation
* Whitespace
* Minor transcription errors

Fuzzy matching allows the system to identify the best candidate rather than requiring exact string equality.

---

### 8.6 Temporal Refinement

The ASR timestamp is treated as a candidate rather than the final frame location.

A local temporal refinement stage is therefore used to improve the estimated onset of the dialogue before frame extraction.

This creates a coarse-to-fine localization process:

```text
ASR
 ↓
Approximate dialogue timestamp
 ↓
Local temporal refinement
 ↓
Final timestamp
```

---

### 8.7 OpenCV

OpenCV was selected for frame-level video access.

It provides:

* FPS retrieval
* Frame count retrieval
* Frame seeking
* Frame reading
* Image writing

The refined timestamp can therefore be mapped to a specific frame.

---

### 8.8 Streamlit

Streamlit was selected for the application interface because it allows the existing Python pipeline to be exposed through a simple interactive UI without requiring a separate frontend framework.

The interface supports:

* Video upload
* Target dialogue input
* Processing status
* Localization metrics
* Extracted frame preview
* JSON result download

The upload limit was configured to support files up to approximately 1 GB.

---

### 8.9 pytest

pytest was selected for automated testing of core project components.

The current test suite validates selected functionality such as:

* Text normalization
* Basic frame/metadata calculations

The final test execution produced:

```text
2 passed
```

---

## 9. Selected Architecture

The validated and implemented architecture is:

```text
                    Input Video
                         │
                         ▼
                  Audio Extraction
                         │
                         ▼
                  Whisper ASR
                         │
                         ▼
              Word-Level Timestamps
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
                Refined Timestamp
                         │
                         ▼
                  Frame Mapping
                         │
                         ▼
                Exact Frame
                         │
                         ▼
             Confidence + JSON
```

The Streamlit interface provides the user-facing layer over this pipeline.

---

## 10. Architecture Rationale

The initial subtitle/OCR-first hypothesis was not supported by the supplied video.

The video contained:

* A usable audio stream
* No separate subtitle stream
* No clearly visible target dialogue text in the sampled frames

Speech recognition therefore provided the most direct available signal for locating the spoken dialogue.

The selected architecture reduces the search problem from the complete video to a much smaller temporal region:

```text
Complete Video
      ↓
Speech Transcription
      ↓
Target Dialogue Match
      ↓
Candidate Time
      ↓
Fine Temporal Refinement
      ↓
Exact Frame
```

---

## 11. Validation Evidence

The technical stack was validated progressively.

### Video

Successfully characterized:

```text
960 × 720
23.976 FPS
76,549 frames
3192.726 seconds
H.264
```

### Audio

Successfully detected and extracted:

```text
AAC
→ WAV
→ Mono
→ 16 kHz
```

### Speech Recognition

Successfully recognized:

```text
"My mind rebels at stagnation."
```

with word-level timestamps.

### Dialogue Matching

Successfully matched the target dialogue against the generated transcription.

### Frame Localization

Successfully converted the refined timestamp into a specific video frame and extracted the frame as an image.

### Application

The complete pipeline was successfully exposed through the Streamlit interface.

---

## 12. Final Stack

The final technology stack is:

```text
Python
│
├── yt-dlp
│     └── Video acquisition
│
├── FFmpeg
│     └── Audio extraction
│
├── Whisper
│     └── Speech recognition + timestamps
│
├── RapidFuzz
│     └── Dialogue matching
│
├── Local temporal refinement
│     └── Speech onset refinement
│
├── OpenCV
│     └── Video/frame processing
│
├── Streamlit
│     └── User interface
│
└── pytest
      └── Automated testing
```

---

## 13. Status

**Technical feasibility validated.**

The ASR-first architecture was selected and implemented.

The final system successfully demonstrates the complete path:

```text
Video
  ↓
Audio
  ↓
Speech Recognition
  ↓
Dialogue Matching
  ↓
Timestamp Localization
  ↓
Temporal Refinement
  ↓
Frame Extraction
  ↓
Result
```

The selected stack provides a practical and reproducible solution for the reference dialogue-localization task.


