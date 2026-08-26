\# Technical Stack Decision



\## Objective



Identify and validate the technical components required to locate a target dialogue in a video and return the corresponding video frame.



\## Feasibility Findings



\### Video



\- Container: MP4

\- Video codec: H.264

\- Resolution: 960x720

\- Frame rate: approximately 23.976 FPS

\- Duration: approximately 3192.73 seconds

\- Frame count: 76,549



\### Audio



\- Codec: AAC

\- Duration: approximately 3192.77 seconds

\- Audio successfully extracted to WAV at 16 kHz mono.



\### Subtitle Availability



FFprobe confirmed that the supplied video contains only:



\- H.264 video stream

\- AAC audio stream



No separate subtitle stream is available.



\### Visual Sampling



A coarse 10-second frame sampling experiment was performed across the video.



The target dialogue was not identified as visible burned-in text. Therefore, OCR was not selected as the primary dialogue localization mechanism.



\### Speech Recognition



OpenAI Whisper was evaluated for speech-to-text localization.



Target dialogue:



> "My mind rebels at stagnation."



The dialogue was successfully recognized.



Word-level timestamps from the ASR feasibility test:



| Word | Start | End |

|---|---:|---:|

| My | 25.280 | 25.460 |

| mind | 25.460 | 25.800 |

| rebels | 25.800 | 26.440 |

| at | 26.440 | 26.940 |

| stagnation | 26.940 | 27.660 |



The ASR test audio began at 300 seconds in the original video.



Therefore, the approximate original-video onset of the target dialogue is:



\*\*325.280 seconds\*\*



\## Technology Decisions



| Component | Selected Technology | Reason |

|---|---|---|

| Programming Language | Python | Suitable ecosystem for audio, video and AI processing |

| Video Acquisition | yt-dlp | Successfully used to acquire the test video |

| Media Processing | FFmpeg | Used successfully for audio extraction and frame extraction |

| Video Processing | OpenCV | Used successfully for video characterization and frame access |

| Speech Recognition | OpenAI Whisper | Successfully recognized the target dialogue |

| Word Timestamps | Whisper word timestamps | Provides temporal localization of individual words |

| Text Matching | RapidFuzz | Planned for robust matching of target dialogue against ASR output |

| Frame Localization | OpenCV | Provides frame-level access for temporal refinement |

| OCR | Optional fallback | Not required as the primary mechanism for the tested video |

| Testing | pytest | Planned for automated component testing |



\## Selected Architecture



The validated direction is:



Video

→ Audio Extraction

→ Whisper Transcription

→ Target Dialogue Matching

→ Word-Level Timestamp

→ Candidate Video Timestamp

→ Frame-Level Temporal Refinement

→ Final Frame



\## Rationale



The initial subtitle/OCR-first hypothesis was not supported by the supplied video.



Speech recognition successfully located the target dialogue, reducing the search space from the complete video to a small temporal region.



The frame-level refinement stage will subsequently convert the ASR candidate timestamp into the final corresponding video frame.



\## Status



\*\*Technical feasibility validated.\*\*



The ASR-first architecture is selected for implementation.

