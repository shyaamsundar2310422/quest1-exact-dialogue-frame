
# Approach

## 1. Overview

Quest1 uses a speech-driven video localization approach to identify the first video frame in which a specified dialogue appears.

The system combines:

- FFmpeg for audio extraction
- Whisper for speech transcription
- Word-level timestamps for temporal localization
- RapidFuzz for dialogue matching
- Local audio analysis for timestamp refinement
- OpenCV for frame extraction
- Confidence scoring for result reliability
- Streamlit for the user interface

The overall pipeline is:

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
Speech Onset Refinement
     │
     ▼
Video Frame Mapping
     │
     ▼
Exact Frame Extraction
     │
     ▼
Confidence Scoring
     │
     ▼
Final Result
````

---

## 2. Input

The system accepts:

### Video

A local video file can be supplied through the command-line interface or uploaded through the Streamlit application.

Supported video formats include:

```text
.mp4
.mkv
.avi
.mov
```

The Streamlit interface supports large video uploads up to approximately 1 GB.

### Target Dialogue

The user provides the dialogue they want to locate.

Example:

```text
My mind rebels at stagnation.
```

The target dialogue is treated as the search query for the transcription stage.

---

## 3. Audio Extraction

The first processing stage extracts the audio track from the video.

FFmpeg is used to convert the audio into a consistent format:

```text
Format: WAV
Channels: Mono
Sample Rate: 16 kHz
```

The extracted audio is then passed to the speech-recognition stage.

This separates audio processing from video processing and provides a standardized input for Whisper.

---

## 4. Speech Transcription

Whisper is used to transcribe the extracted audio.

The system uses the English-specific:

```text
tiny.en
```

model.

Word-level timestamps are enabled during transcription.

Conceptually, the output contains information such as:

```text
Word                  Start       End

My                    325.100     ...
mind                  ...         ...
rebels                ...         ...
at                    ...         ...
stagnation            ...         ...
```

The word timestamps provide the temporal information required to locate the dialogue within the video.

---

## 5. Dialogue Matching

The transcription is searched for the target dialogue.

Before comparison, both the target dialogue and transcription text are normalized.

Normalization includes:

* Converting text to lowercase
* Removing unnecessary leading/trailing whitespace
* Normalizing whitespace

RapidFuzz is then used to calculate similarity between the target dialogue and available transcription segments.

The highest-scoring candidate is selected.

The matcher returns information including:

```text
Matched text
Match score
Segment timing
Word timing information
```

A threshold is used to determine whether the match is sufficiently similar to the requested dialogue.

---

## 6. Candidate Timestamp Selection

Once the best dialogue match is identified, the system determines an initial candidate timestamp.

Word-level timing is preferred because it provides finer temporal resolution.

The timestamp selection logic is:

```text
If word timestamps are available:
        use the first matched word's start time

Otherwise:
        use the matched segment's start time
```

For example:

```text
Candidate timestamp = 325.100s
```

This timestamp represents the estimated beginning of the target dialogue.

---

## 7. Temporal Refinement

The ASR timestamp is treated as an initial estimate rather than the final frame location.

A local audio analysis step refines the speech onset around the candidate timestamp.

The refinement process can be represented as:

```text
Candidate timestamp
        │
        ▼
Local audio region
        │
        ▼
Speech onset analysis
        │
        ▼
Refined timestamp
```

For the reference validation case:

```text
Candidate timestamp = 325.100s
Refined timestamp   = 325.250s
```

The refined timestamp is used for the final frame extraction stage.

---

## 8. Timestamp-to-Frame Mapping

The refined timestamp must be converted into a video frame position.

OpenCV is used to obtain the video's frame rate.

The frame number is calculated as:

```text
frame_number = round(timestamp × FPS)
```

For example:

```text
Timestamp = 325.250 seconds
FPS       = 23.976...
```

The resulting frame number identifies the video frame corresponding to the refined dialogue onset.

The calculated frame number is also bounded by the available frame range of the video.

---

## 9. Exact Frame Extraction

OpenCV is used to retrieve the calculated frame.

The extraction process is:

```text
Open video
     ↓
Read FPS and frame count
     ↓
Calculate target frame
     ↓
Seek to frame
     ↓
Read frame
     ↓
Save frame as image
```

The resulting image represents the localized dialogue frame.

---

## 10. Confidence Scoring

A confidence score is calculated after localization.

The score considers:

* Dialogue matching quality
* Difference between the candidate timestamp and refined timestamp

The confidence value is intended as a practical reliability indicator for the localization result.

It is not treated as a statistically calibrated probability.

The final result includes:

```text
Match Score
Confidence
Candidate Timestamp
Refined Timestamp
Frame Number
Frame Timestamp
```

---

## 11. Final Output

The system produces a structured localization result.

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
  "fps": 23.976043434000623,
  "confidence": 100.0
}
```

The extracted frame is also saved as an image.

---

## 12. User Interface

The Streamlit interface provides a graphical workflow over the same localization pipeline.

The user can:

1. Upload a video.
2. Enter the target dialogue.
3. Start localization.
4. Observe processing stages.
5. View the localization metrics.
6. View the extracted frame.
7. Download the result as JSON.

The interface does not implement a separate localization algorithm.

Instead, it acts as a presentation layer over the existing processing components.

---

## 13. Processing Architecture

The system is divided into modular components.

```text
src/
├── acquisition/
│   └── video_downloader.py
│
├── matching/
│   └── text_matcher.py
│
├── search/
│   ├── coarse_search.py
│   └── fine_search.py
│
├── confidence/
│   └── scorer.py
│
├── video/
│   ├── frame_extractor.py
│   ├── metadata.py
│   ├── characterize.py
│   ├── dense_sample.py
│   ├── extract_samples.py
│   └── refine_frame.py
│
├── pipeline/
│   └── localize_dialogue.py
│
└── output/
    └── result_writer.py
```

This modular structure separates individual responsibilities and makes the system easier to test and extend.

---

## 14. End-to-End Execution

The complete localization process can be summarized as:

```text
                USER
                  │
                  ▼
        Video + Target Dialogue
                  │
                  ▼
          ┌─────────────────┐
          │ Audio Extraction│
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Whisper ASR     │
          │ + Word Timing   │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Fuzzy Matching  │
          └────────┬────────┘
                   │
                   ▼
          Candidate Timestamp
                   │
                   ▼
          ┌─────────────────┐
          │ Temporal        │
          │ Refinement      │
          └────────┬────────┘
                   │
                   ▼
          Refined Timestamp
                   │
                   ▼
          ┌─────────────────┐
          │ OpenCV Frame    │
          │ Extraction      │
          └────────┬────────┘
                   │
                   ▼
          Exact Dialogue Frame
                   │
                   ▼
          Confidence + JSON
                   │
                   ▼
               USER
```

---

## 15. Design Rationale

The approach is based on the observation that the target information is spoken dialogue.

Instead of scanning every video frame with expensive visual processing, the system first uses the audio channel to narrow down the temporal location.

This provides a more practical search strategy:

```text
Speech
  ↓
Text
  ↓
Time
  ↓
Frame
```

Whisper provides the connection between speech and time, fuzzy matching handles minor transcription differences, temporal refinement improves the timestamp, and OpenCV converts the final timestamp into the required video frame.

---

## 16. Validation

The approach was validated using the reference dialogue:

```text
My mind rebels at stagnation.
```

The system successfully produced:

```text
Match score:          100.00
Candidate timestamp:  325.100s
Refined timestamp:    325.250s
```

The corresponding video frame was successfully extracted and presented through the application.

Automated tests were also added for selected core components.

```text
2 passed
```

---

## 17. Current Limitations

The current approach has several limitations:

* Whisper transcription is computationally expensive on CPU.
* Processing long videos can take several minutes.
* The current configuration is optimized for English dialogue.
* ASR accuracy depends on audio quality.
* The confidence score is heuristic.
* Visual mouth-movement verification is not currently part of the localization pipeline.
* The system is designed for offline/local processing rather than real-time operation.

---

## 18. Future Improvements

Possible improvements include:

* GPU-accelerated Whisper inference
* Faster ASR models
* Transcript caching
* Parallel audio processing
* Improved speech-onset detection
* Better confidence calibration
* Visual verification of the detected speaker
* Subtitle-assisted localization when subtitles are available
* Support for multiple target dialogues
* Batch processing of multiple videos
* Production-scale processing

---

## 19. Summary

The final approach uses a coarse-to-fine temporal localization strategy:

```text
Video
  ↓
Audio
  ↓
ASR
  ↓
Dialogue Match
  ↓
Approximate Time
  ↓
Fine Temporal Refinement
  ↓
Exact Video Frame
```

The key principle is to first locate the dialogue in time using speech information and then map the refined timestamp to the corresponding video frame.
