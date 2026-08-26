
# Development Log

## 1. Project Initialization

The project was initialized with a modular Python structure separating video processing, matching, search, confidence scoring, output generation, and documentation.

The initial repository structure was created to support incremental development and validation.

### Initial goals

- Analyze the reference video.
- Determine how dialogue could be localized.
- Select an appropriate technical approach.
- Build the localization pipeline incrementally.
- Validate each major component.
- Provide a usable interface.
- Document the development process.

---

## 2. Video Characterization

The reference video was analyzed before implementation to understand the available signals and determine the feasibility of different localization approaches.

The investigation considered:

- Video duration
- Frame rate
- Resolution
- Audio availability
- Subtitle availability
- Dialogue characteristics
- Speech timing
- Frame-level localization requirements

The video characterization showed that speech/audio was available and could be used as a strong localization signal.

The analysis also established that the target dialogue:

```text
My mind rebels at stagnation.
````

appears in the reference video and could be used as the primary validation case.

---

## 3. Initial Localization Considerations

Several possible signals were considered for identifying the target dialogue:

* Subtitle text
* On-screen text/OCR
* Audio transcription
* Visual analysis

Subtitle-based localization was investigated first because subtitles can provide direct text-to-time mappings.

However, the reference video did not provide a reliable subtitle track that could be directly used for the task.

This made a subtitle-dependent solution unsuitable as the primary approach.

---

## 4. ASR-Based Approach

Because the target information was spoken dialogue and usable subtitles were unavailable, automatic speech recognition was selected as the primary localization method.

The selected approach was:

```text
Video
  ↓
Audio extraction
  ↓
Speech transcription
  ↓
Dialogue matching
  ↓
Candidate timestamp
  ↓
Timestamp refinement
  ↓
Video frame extraction
```

This approach allows the system to operate directly from the video's audio.

---

## 5. Whisper Evaluation and Integration

Whisper was selected as the speech recognition component.

The important requirement was not only transcription accuracy but also access to timing information.

Word-level timestamps were therefore enabled.

The transcription stage was implemented to:

1. Load the Whisper model.
2. Process the extracted audio.
3. Generate English transcription.
4. Request word-level timestamps.
5. Return the resulting transcription structure.

The `tiny.en` model was selected because the reference dialogue is in English and the project needs to remain practical for local CPU execution.

---

## 6. Audio Extraction

FFmpeg was integrated to extract the audio track from the input video.

The extracted audio is converted to:

* WAV
* Mono
* 16 kHz

This provides a consistent audio representation for the transcription stage.

The audio extraction step was separated from transcription so that the processing pipeline remained modular.

---

## 7. Dialogue Matching

After transcription was implemented, the next requirement was locating the target dialogue within the generated transcript.

Exact string matching was considered insufficient because ASR output can contain minor differences.

Examples include:

```text
My mind rebels at stagnation.
```

and:

```text
my mind rebels at stagnation
```

or small transcription variations.

RapidFuzz was therefore integrated for fuzzy text matching.

The matching process:

1. Normalizes the target dialogue.
2. Normalizes transcription text.
3. Compares the target against available transcript segments.
4. Selects the highest-scoring match.
5. Returns the matching score and timing information.

---

## 8. Candidate Timestamp Localization

Once the best dialogue segment was identified, a candidate timestamp was required.

Word-level timestamps were preferred over segment-level timestamps.

The implementation uses the first word's start timestamp when word-level timing information is available.

If word-level timestamps are unavailable, the system falls back to the segment start timestamp.

This produced a candidate point close to the beginning of the target dialogue.

---

## 9. Timestamp Refinement

ASR timestamps provide a useful estimate but may not represent the exact onset of speech.

A refinement stage was therefore introduced.

The candidate timestamp is passed to the temporal refinement component, which analyzes the local audio region to estimate a more precise speech onset.

The resulting workflow became:

```text
Whisper timestamp
      ↓
Candidate timestamp
      ↓
Local temporal refinement
      ↓
Refined timestamp
```

This refined timestamp is then used for frame localization.

---

## 10. Video Frame Mapping

After obtaining the refined timestamp, the system maps the timestamp to a video frame.

The video's FPS is obtained using OpenCV.

The frame position is calculated using:

```text
frame_number = round(timestamp × FPS)
```

The corresponding frame is then extracted from the video.

The implementation also checks the valid frame range to prevent attempts to access frames outside the video.

---

## 11. Exact Frame Extraction

OpenCV was used to retrieve and save the localized frame.

The frame extraction stage:

1. Opens the input video.
2. Reads the FPS and frame count.
3. Calculates the target frame number.
4. Seeks to the target frame.
5. Reads the frame.
6. Saves the frame as an image.

The extracted frame provides visual evidence for the localization result.

---

## 12. End-to-End Pipeline Integration

After the individual components were implemented, they were integrated into a single localization pipeline.

The final processing sequence became:

```text
[1] Extract audio
        ↓
[2] Transcribe audio
        ↓
[3] Match target dialogue
        ↓
[4] Refine timestamp
        ↓
[5] Extract exact frame
        ↓
    Confidence scoring
        ↓
    Structured result
```

The pipeline was exposed through a command-line entry point for direct execution and validation.

---

## 13. Initial Integration Issue

During integration, the pipeline encountered a timestamp field mismatch.

The implementation initially expected a field named:

```text
word_start
```

while the actual transcription/matching result exposed word timing information through the `words` structure.

This resulted in:

```text
KeyError: 'word_start'
```

The issue was corrected by retrieving the start time from the matched word:

```python
words = match.get("words", [])

if words:
    candidate_time = words[0].get("start")
else:
    candidate_time = match.get("segment_start")
```

This made the timestamp extraction compatible with the actual transcription structure.

---

## 14. Successful End-to-End Validation

After correcting the timestamp handling, the complete pipeline was executed successfully against the reference video.

The system produced:

```text
Matched text:
My mind rebels at stagnation.

Match score:
100.00

Candidate timestamp:
325.100s

Refined timestamp:
325.250s
```

The system then successfully mapped the refined timestamp to a video frame and extracted the corresponding image.

The successful run confirmed that the major processing stages could operate together.

---

## 15. Confidence Scoring

A confidence scoring component was added to provide an additional indication of localization reliability.

The score considers the dialogue matching result and the relationship between the candidate and refined timestamps.

The confidence value is included in the final structured output and displayed by the Streamlit interface.

---

## 16. Command-Line Interface

The core localization workflow was exposed through a command-line interface.

The CLI accepts:

* Video path
* Target dialogue
* Whisper model path
* Output directory

This allowed the pipeline to be tested independently of the graphical interface.

---

## 17. Streamlit Interface

After validating the core pipeline, a Streamlit interface was added.

The interface provides:

* Video upload
* Target dialogue input
* Processing status
* Match score
* Refined timestamp
* Confidence score
* Frame number
* Frame timestamp
* Extracted frame preview
* JSON result download

The UI was intentionally kept lightweight so that it could directly use the existing Python processing components.

---

## 18. Large Video Upload Support

The reference video used during testing was substantially larger than Streamlit's default upload limit.

The application upload configuration was therefore adjusted to support files up to approximately 1 GB.

This allows the actual reference video to be processed through the UI rather than requiring a separate preprocessing step.

---

## 19. Whisper Model Caching

During UI testing, processing a long video required significant time because speech transcription was performed locally on the CPU.

The Whisper model loading step was identified as unnecessary repeated overhead during Streamlit reruns.

Streamlit's resource caching mechanism was therefore introduced:

```python
@st.cache_resource
def load_whisper_model(model_path):
    return whisper.load_model(model_path)
```

The transcription function was updated to use the cached model loader.

This reduced repeated model-loading overhead for subsequent Streamlit interactions.

---

## 20. Performance Observation

The reference video required approximately 10 minutes for complete processing on the development machine.

The primary performance bottleneck is local Whisper transcription on CPU rather than the dialogue matching or frame extraction stages.

The current implementation therefore prioritizes:

* Correctness
* Reproducibility
* Local execution
* Frame-level localization

over real-time processing.

Potential future performance improvements include:

* GPU-based inference
* Faster ASR models
* Audio chunking
* Parallel processing
* Transcript caching
* More efficient inference settings

---

## 21. Testing

Automated tests were added for core functionality.

The test suite was executed using:

```bash
pytest tests -vv
```

The final test execution produced:

```text
tests/test_matching.py::test_normalize PASSED
tests/test_metadata.py::test_basic_metadata PASSED

2 passed
```

The tests validate selected core components independently of the full video-processing pipeline.

---

## 22. Documentation

Documentation was progressively added to record:

* Business requirements
* Technical requirements
* Project approach
* Design decisions
* Technology selection
* Video characterization
* Testing
* Development history
* AI-assisted development prompts

The README was subsequently updated and polished to provide an overview of the final project and instructions for understanding and using the repository.

---

## 23. Final Development State

The final system provides an end-to-end workflow:

```text
Input Video
    ↓
Audio Extraction
    ↓
Whisper Transcription
    ↓
Fuzzy Dialogue Matching
    ↓
Candidate Timestamp
    ↓
Temporal Refinement
    ↓
Frame Mapping
    ↓
Exact Frame Extraction
    ↓
Confidence Scoring
    ↓
Streamlit Result
```

The reference dialogue:

```text
"My mind rebels at stagnation."
```

was successfully localized, with the pipeline producing a matching score of 100.00%, a candidate timestamp of approximately 325.100 seconds, and a refined timestamp of approximately 325.250 seconds.

The project was then validated through the Streamlit interface and automated tests.

---

## 24. Current Limitations

The current prototype has several known limitations:

* Long videos can require significant CPU processing time.
* ASR accuracy depends on audio quality.
* The current implementation is optimized for English dialogue.
* The system is not designed for real-time processing.
* Visual verification of the speaker's mouth movement is not currently part of the localization algorithm.
* The confidence score is a heuristic indicator rather than a statistically calibrated probability.

These limitations are documented so that future improvements can be evaluated against the current baseline.

---

## 25. Future Development

Potential future development includes:

1. GPU-accelerated ASR.
2. Faster speech-recognition models.
3. Parallel audio processing.
4. Transcript caching.
5. Support for multiple dialogue queries.
6. Improved confidence calibration.
7. Optional subtitle-based localization when subtitle tracks are available.
8. Visual verification around the detected frame.
9. Scalable processing for multiple videos.
10. Production deployment with dedicated backend processing.

---

## 26. Development Summary

The project evolved from initial feasibility analysis into a complete dialogue-to-frame localization system.

The major progression was:

```text
Requirement Analysis
        ↓
Video Characterization
        ↓
Localization Signal Evaluation
        ↓
ASR Selection
        ↓
Whisper Integration
        ↓
Dialogue Matching
        ↓
Timestamp Refinement
        ↓
Frame Localization
        ↓
Confidence Scoring
        ↓
CLI Integration
        ↓
Streamlit UI
        ↓
Performance Optimization
        ↓
Testing
        ↓
Documentation
```

The final implementation provides a reproducible automated method for locating a specified spoken dialogue at frame level within a video.

```

