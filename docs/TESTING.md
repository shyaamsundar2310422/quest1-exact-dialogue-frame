
# Testing

## 1. Testing Overview

Testing was performed at multiple stages of development to validate the Quest1 Exact Dialogue Frame Detection system.

The testing strategy covered:

1. Video characterization
2. Individual component validation
3. End-to-end pipeline validation
4. Streamlit UI validation
5. Automated unit tests
6. Error and input validation
7. Performance observation

The primary validation target was the reference dialogue:

```text
My mind rebels at stagnation.
````

---

## 2. Test Environment

The application was tested in a local Python virtual environment.

### Main Technologies

* Python
* FFmpeg
* Whisper
* OpenCV
* RapidFuzz
* Streamlit
* pytest

The reference video was approximately:

```text
Duration: 3192.73 seconds
Resolution: 960 × 720
Codec: H.264
Frame rate: approximately 23.976 FPS
```

The video contained:

* One H.264 video stream
* One AAC audio stream
* No usable subtitle track

The absence of subtitles led to the selection of an ASR-based localization approach.

---

## 3. Video Characterization Testing

Before implementing the final localization pipeline, the reference video was analyzed to determine whether the required signals were available.

The following properties were successfully obtained:

```text
FPS:
23.97606434000623

Frame count:
76549

Duration:
3192.7258333333334 seconds

Width:
960

Height:
720

Codec:
H.264
```

The video also contained an AAC audio stream.

This confirmed that the video contained an audio signal suitable for speech recognition.

---

## 4. Subtitle Availability Test

The video was inspected for subtitle streams.

The available streams were:

```text
index=0 codec_name=h264 codec_type=video
index=1 codec_name=aac  codec_type=audio
```

No subtitle stream was available.

Therefore, a subtitle-dependent localization solution was not suitable for the reference video.

The project proceeded with automatic speech recognition.

---

## 5. Audio Extraction Test

FFmpeg was used to extract the audio track.

The extraction configuration was:

```text
Format: WAV
Channels: Mono
Sample Rate: 16000 Hz
```

The extracted audio was successfully passed to the Whisper transcription stage.

---

## 6. Whisper Transcription Test

Whisper was tested against the extracted reference audio.

The transcription successfully identified the target dialogue:

```text
My mind rebels at stagnation.
```

Word-level timestamps were enabled to provide more precise temporal information.

The successful transcription established that ASR could provide a usable temporal signal for the localization task.

---

## 7. Dialogue Matching Test

The generated transcription was searched using the target dialogue:

```text
My mind rebels at stagnation.
```

The matching component successfully identified the corresponding transcription segment.

The validated result was:

```text
Matched text:
My mind rebels at stagnation.

Match score:
100.00
```

This confirmed that the fuzzy matching stage could successfully locate the target dialogue in the transcription.

---

## 8. Candidate Timestamp Test

The matched dialogue contained word-level timing information.

The first matched word's start timestamp was used as the candidate dialogue onset.

Validated result:

```text
Candidate timestamp:
325.100s
```

The implementation also contains a fallback to the segment start timestamp when word-level timestamps are unavailable.

---

## 9. Timestamp Refinement Test

The candidate timestamp was passed through the local temporal refinement stage.

Validated result:

```text
Candidate timestamp:
325.100s

Refined timestamp:
325.250s
```

This confirmed that the refinement stage was able to produce a usable timestamp for subsequent frame extraction.

---

## 10. Frame Localization Test

The refined timestamp was converted to a frame number using the video's FPS.

The validated frame result was:

```text
Frame number:
7798
```

The corresponding frame timestamp was approximately:

```text
325.241s
```

The frame was successfully extracted and written as an image.

---

## 11. End-to-End Test

The complete pipeline was executed using the reference video and target dialogue.

### Input

```text
Target dialogue:
My mind rebels at stagnation.
```

### Processing

```text
Video
  ↓
Audio extraction
  ↓
Whisper transcription
  ↓
Dialogue matching
  ↓
Candidate timestamp
  ↓
Temporal refinement
  ↓
Frame extraction
  ↓
Confidence calculation
  ↓
Result generation
```

### Result

```text
Matched text:
My mind rebels at stagnation.

Match score:
100.00

Candidate timestamp:
325.100s

Refined timestamp:
325.250s

Frame number:
7798
```

The extracted frame was successfully generated.

This validated the complete path from video input to exact frame output.

---

## 12. Confidence Score Test

The confidence scoring component was integrated into the final pipeline.

The confidence calculation uses the dialogue match quality and the relationship between the candidate and refined timestamps.

The confidence value is included in:

* CLI output
* Streamlit output
* JSON result

The confidence value is treated as a heuristic reliability indicator rather than a statistically calibrated probability.

---

## 13. Automated Unit Tests

Automated tests were added for selected core components.

The test suite can be executed using:

```bash
pytest tests -vv
```

The final test execution produced:

```text
tests/test_matching.py::test_normalize PASSED
tests/test_metadata.py::test_basic_metadata PASSED

2 passed
```

### Test 1 — Text Normalization

The matching test verifies that normalization handles differences in:

* Capitalization
* Leading/trailing whitespace
* Internal whitespace

Example:

```text
"  Hello   WORLD  "
```

is normalized to:

```text
"hello world"
```

### Test 2 — Basic Metadata / Frame Calculation

The metadata test validates basic assumptions used during frame localization:

* FPS is positive.
* Frame number is non-negative.
* Calculated frame timestamp is positive.

---

## 14. Streamlit UI Test

The complete application was tested through the Streamlit interface.

The following workflow was validated:

```text
1. Launch Streamlit
2. Upload reference video
3. Enter target dialogue
4. Click Locate Dialogue
5. Observe processing status
6. Wait for transcription and localization
7. View match score
8. View refined timestamp
9. View confidence
10. View frame number
11. View extracted frame
12. Download JSON result
```

The complete workflow executed successfully.

---

## 15. Large File Upload Test

The reference video was approximately 0.9 GB.

The default Streamlit upload limit was insufficient for the reference input.

The server configuration was therefore changed to:

```toml
[server]
maxUploadSize = 1024
```

This increased the supported upload size to approximately 1 GB.

The reference video was successfully uploaded through the Streamlit interface after this configuration change.

---

## 16. Whisper Model Caching Test

The Streamlit application was updated to cache the Whisper model using:

```python
@st.cache_resource
def load_whisper_model(model_path):
    return whisper.load_model(model_path)
```

The application was tested after this modification.

The reference video processing time decreased from approximately:

```text
13 minutes
```

to approximately:

```text
10 minutes
```

The exact processing time depends on the local machine and runtime conditions.

The primary remaining bottleneck is CPU-based Whisper transcription.

---

## 17. Input Validation Testing

The Streamlit application includes validation for required inputs.

### Missing Video

Expected behavior:

```text
Please upload a video.
```

### Missing Target Dialogue

Expected behavior:

```text
Please enter the target dialogue.
```

### Missing Whisper Model

Expected behavior:

```text
Whisper model not found.
```

The application does not proceed with localization when required inputs are unavailable.

---

## 18. Dialogue Not Found Handling

If the target dialogue cannot be found in the transcription, the system does not attempt to generate an arbitrary frame.

Instead, the localization process reports:

```text
The target dialogue could not be found in the transcription.
```

This prevents an invalid match from being presented as a successful localization.

---

## 19. Frame Extraction Failure Handling

The frame extraction component validates that:

* The video can be opened.
* The calculated frame number is within the valid frame range.
* The requested frame can be successfully read.

If frame extraction fails, the system raises an error rather than returning an invalid image.

---

## 20. Repository Validation

Before final submission, the Git repository was checked for:

* Untracked runtime artifacts
* Large video files
* Local Whisper model files
* Python virtual environment files
* Generated output files
* Python cache files

The `.gitignore` configuration excludes these local/runtime artifacts.

The final repository was verified using:

```bash
git status
```

The final state was:

```text
nothing to commit, working tree clean
```

The local branch was synchronized with the GitHub repository.

---

## 21. Test Results Summary

| Test Area                      | Result         |
| ------------------------------ | -------------- |
| Video characterization         | PASS           |
| Audio stream detection         | PASS           |
| Subtitle availability check    | PASS           |
| Audio extraction               | PASS           |
| Whisper transcription          | PASS           |
| Dialogue matching              | PASS           |
| Candidate timestamp extraction | PASS           |
| Timestamp refinement           | PASS           |
| Frame localization             | PASS           |
| Exact frame extraction         | PASS           |
| Confidence calculation         | PASS           |
| End-to-end pipeline            | PASS           |
| Streamlit UI                   | PASS           |
| 1 GB video upload              | PASS           |
| Whisper model caching          | PASS           |
| Automated tests                | PASS — 2 tests |
| Git repository validation      | PASS           |

---

## 22. Known Limitations

The current testing process has some limitations.

### Limited Automated Test Coverage

Only selected core components currently have automated unit tests.

The full video localization workflow has primarily been validated through end-to-end execution using the reference video.

### CPU Processing Time

The reference video requires several minutes for complete processing because Whisper transcription is performed locally on CPU.

### ASR Dependence

The quality of dialogue localization depends partly on the accuracy of speech recognition.

Background noise, unclear speech, accents, or poor audio quality can affect transcription.

### English-Focused Validation

The primary validation case uses English dialogue and the `tiny.en` Whisper model.

---

## 23. Future Testing

Future testing could expand coverage to include:

* Multiple video formats
* Different frame rates
* Different resolutions
* No-audio videos
* Noisy audio
* Multiple dialogue occurrences
* Similar dialogue phrases
* Incorrect target dialogue
* Very short videos
* Very long videos
* Multiple languages
* GPU-based execution
* Larger automated end-to-end test coverage

---

## 24. Final Validation Case

The primary validated test case is:

```text
Video:
Reference video

Target:
"My mind rebels at stagnation."

Expected behavior:
Locate the dialogue and extract the corresponding video frame.

Observed:
Match score = 100.00
Candidate timestamp = 325.100s
Refined timestamp = 325.250s
Frame number = 7798

Status:
PASS
```

This test case demonstrates that the implemented pipeline can successfully transform a natural-language dialogue query into a specific, verifiable video frame.


