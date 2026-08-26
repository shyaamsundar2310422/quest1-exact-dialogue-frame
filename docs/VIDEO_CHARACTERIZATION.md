
# Video Characterization

## 1. Input

### Video URL

```text
https://ok.ru/video/248244667877
````

### Target Dialogue

```text
"My mind rebels at stagnation"
```

---

## 2. Video Metadata

The downloaded reference video was characterized to determine its technical properties and suitability for frame-level processing.

| Property    |   Observed Value |
| ----------- | ---------------: |
| Resolution  |        960 × 720 |
| FPS         |        23.976064 |
| Frame Count |           76,549 |
| Duration    | 3192.726 seconds |
| Codec       |            H.264 |

### Derived Duration

The video duration is approximately:

```text
3192.726 seconds
≈ 53.21 minutes
```

---

## 3. Frame Timing Characteristics

The approximate duration represented by one frame is:

```text
1 / 23.976064 ≈ 0.0417 seconds
```

Therefore, consecutive frames are approximately:

```text
41.7 milliseconds
```

apart.

This provides the temporal resolution available for frame-level localization.

---

## 4. Video Acquisition

The video was successfully obtained from the supplied OK.ru URL using `yt-dlp`.

### Acquisition Issue

Initial format discovery encountered a local SSL certificate verification issue.

Format discovery succeeded when certificate verification was disabled for the diagnostic/download experiment.

### Final Application Consideration

Certificate verification will **not** be disabled in the final application.

The diagnostic workaround was used only during the acquisition/feasibility investigation.

---

## 5. Stream Characterization

The downloaded video was inspected to determine the available media streams.

The observed streams were:

```text
index=0 codec_name=h264 codec_type=video
index=1 codec_name=aac  codec_type=audio
```

Therefore, the video contains:

* H.264 video
* AAC audio

The presence of an audio stream makes the video suitable for speech-based dialogue localization.

---

## 6. Visual Characterization

Representative frames were extracted from the video to inspect the visual content and determine whether the target dialogue could be localized through visible on-screen text.

The preliminary visual inspection showed the underlying video scene but did not visibly contain the target dialogue text.

Therefore, the target dialogue was not treated as directly available through visible text in the sampled frames.

---

## 7. Initial Visual Sampling

A preliminary sample of frames from approximately:

```text
305–320 seconds
```

was extracted based on an external subtitle timing reference.

The sampled frames showed the underlying video scene but did not visibly contain the target dialogue text.

### Important Observation

The external subtitle timing reference was **not** treated as ground truth for the downloaded video.

This distinction was maintained because the external timing reference could not be assumed to correspond exactly to the downloaded video's frame timing.

Further investigation was therefore required to determine the actual location of the target dialogue.

---

## 8. Subtitle Availability

The downloaded video was inspected for subtitle streams.

The available media streams were:

```text
index=0 codec_name=h264 codec_type=video
index=1 codec_name=aac  codec_type=audio
```

No subtitle stream was available.

Therefore, a subtitle-dependent localization approach could not be used as the primary method for this video.

This led to further evaluation of the video's audio as a localization signal.

---

## 9. Audio-Based Localization Feasibility

Since the video contains an AAC audio stream and no usable subtitle stream, the audio channel provides a viable source for identifying the spoken dialogue.

The resulting direction was:

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
Frame Extraction
```

This approach avoids requiring subtitles to be embedded in the source video.

---

## 10. OCR Feasibility

OCR was considered as a potential method for detecting visible dialogue text.

However, the preliminary frame samples did not show the target dialogue as visible text.

Therefore, full-video OCR was not selected as the primary dialogue localization mechanism.

OCR-related components remain available in the project for potential visual analysis or future extensions.

---

## 11. Search Strategy Implications

The video contains approximately:

```text
76,549 frames
```

At approximately:

```text
23.976 FPS
```

performing expensive visual OCR processing independently on every frame would be computationally inefficient.

The characterization therefore supports a **coarse-to-fine localization strategy**.

The intended strategy is:

```text
Coarse temporal localization
        ↓
Candidate dialogue region
        ↓
Fine temporal refinement
        ↓
Exact frame extraction
```

The final implementation uses the audio channel to perform the initial temporal localization and then maps the refined timestamp to a video frame.

---

## 12. Characterization Findings

The characterization established the following:

| Finding                                           | Result       |
| ------------------------------------------------- | ------------ |
| Video successfully acquired                       | Yes          |
| Video stream available                            | Yes          |
| Audio stream available                            | Yes          |
| Subtitle stream available                         | No           |
| Target dialogue visibly present in sampled frames | Not observed |
| Frame-level processing feasible                   | Yes          |
| Full-video OCR considered efficient               | No           |
| Audio-based localization feasible                 | Yes          |

---

## 13. Final Characterization Conclusion

The reference video is suitable for frame-level dialogue localization.

Its approximately 76,549 frames and approximately 23.976 FPS provide sufficient temporal resolution for identifying a specific frame.

The absence of a usable subtitle stream ruled out a subtitle-dependent approach.

Preliminary visual sampling also did not show the target dialogue as visible on-screen text.

Therefore, the audio channel was selected as the primary localization signal.

The resulting technical direction was:

```text
Input Video
     ↓
Audio Extraction
     ↓
Speech Recognition
     ↓
Dialogue Matching
     ↓
Candidate Timestamp
     ↓
Fine Temporal Refinement
     ↓
Video Frame Mapping
     ↓
Exact Dialogue Frame
```

This characterization formed the basis for the subsequent technical design and implementation decisions documented in:

* `TECH_STACK_DECISION.md`
* `APPROACH.md`
* `DESIGN_DECISIONS.md`
* `DEVELOPMENT_LOG.md`


