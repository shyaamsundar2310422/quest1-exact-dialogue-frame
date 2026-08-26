import json
import os
import shutil
import tempfile

import streamlit as st

from src.pipeline.localize_dialogue import (
    extract_audio,
    transcribe,
    extract_frame,
)
from src.matching.text_matcher import find_dialogue
from src.search.fine_search import refine_speech_onset
from src.confidence.scorer import calculate_confidence


MODEL_PATH = "models/tiny.en.pt"


st.set_page_config(
    page_title="Quest1 Dialogue Locator",
    page_icon="🎬",
    layout="wide",
)


st.title("🎬 Quest1 Exact Dialogue Frame Locator")

st.write(
    "Upload a video, enter a target dialogue, and locate "
    "the corresponding video frame."
)

st.divider()

uploaded_video = st.file_uploader(
    "Upload Video",
    type=["mp4", "mkv", "avi", "mov"],
)

target_dialogue = st.text_input(
    "Target Dialogue",
    placeholder="e.g. My mind rebels at stagnation."
)

locate_button = st.button(
    "🔎 Locate Dialogue",
    type="primary",
    use_container_width=True,
)


if locate_button:

    if uploaded_video is None:
        st.error("Please upload a video.")

    elif not target_dialogue.strip():
        st.error("Please enter the target dialogue.")

    elif not os.path.exists(MODEL_PATH):
        st.error(
            "Whisper model not found. "
            f"Expected: {MODEL_PATH}"
        )

    else:

        try:
            with tempfile.TemporaryDirectory() as temp_dir:

                video_path = os.path.join(
                    temp_dir,
                    uploaded_video.name
                )

                audio_path = os.path.join(
                    temp_dir,
                    "audio.wav"
                )

                frame_path = os.path.join(
                    temp_dir,
                    "exact_dialogue_frame.jpg"
                )

                with open(video_path, "wb") as f:
                    f.write(uploaded_video.getbuffer())

                # ---------------------------------------------
                # 1. Extract audio
                # ---------------------------------------------

                with st.status(
                    "Processing video...",
                    expanded=True
                ) as status:

                    st.write("Extracting audio...")

                    extract_audio(
                        video_path,
                        audio_path
                    )

                    # -----------------------------------------
                    # 2. Whisper
                    # -----------------------------------------

                    st.write(
                        "Transcribing audio with Whisper..."
                    )

                    result = transcribe(
                        audio_path,
                        MODEL_PATH
                    )

                    # -----------------------------------------
                    # 3. Match dialogue
                    # -----------------------------------------

                    st.write(
                        "Searching for target dialogue..."
                    )

                    match = find_dialogue(
                        result,
                        target_dialogue
                    )

                    if match is None:
                        status.update(
                            label="Dialogue not found",
                            state="error"
                        )

                        st.error(
                            "The target dialogue could not "
                            "be found in the transcription."
                        )

                        st.stop()

                    words = match.get("words", [])

                    if words:
                        candidate_time = words[0].get(
                            "start"
                        )
                    else:
                        candidate_time = match.get(
                            "segment_start"
                        )

                    if candidate_time is None:
                        raise RuntimeError(
                            "No usable timestamp found."
                        )

                    # -----------------------------------------
                    # 4. Fine refinement
                    # -----------------------------------------

                    st.write(
                        "Refining dialogue timestamp..."
                    )

                    refined_time = refine_speech_onset(
                        audio_path,
                        candidate_time
                    )

                    # -----------------------------------------
                    # 5. Frame extraction
                    # -----------------------------------------

                    st.write(
                        "Extracting corresponding frame..."
                    )

                    frame_number, fps = extract_frame(
                        video_path,
                        refined_time,
                        frame_path
                    )

                    confidence = calculate_confidence(
                        match["score"],
                        candidate_time,
                        refined_time
                    )

                    status.update(
                        label="Localization complete",
                        state="complete"
                    )

                # ---------------------------------------------
                # Results
                # ---------------------------------------------

                st.divider()

                st.subheader("Localization Result")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Match Score",
                        f"{match['score']:.2f}%"
                    )

                with col2:
                    st.metric(
                        "Refined Timestamp",
                        f"{refined_time:.3f}s"
                    )

                with col3:
                    st.metric(
                        "Confidence",
                        f"{confidence:.2f}%"
                    )

                st.write(
                    f"**Matched Text:** {match['text']}"
                )

                st.write(
                    f"**Frame Number:** {frame_number}"
                )

                st.write(
                    f"**Frame Timestamp:** "
                    f"{frame_number / fps:.3f}s"
                )

                st.image(
                    frame_path,
                    caption=(
                        "Detected dialogue frame"
                    ),
                    use_container_width=True
                )

                result_data = {
                    "target": target_dialogue,
                    "matched_text": match["text"],
                    "match_score": match["score"],
                    "candidate_timestamp": candidate_time,
                    "refined_timestamp": refined_time,
                    "frame_number": frame_number,
                    "frame_timestamp": frame_number / fps,
                    "fps": fps,
                    "confidence": confidence,
                }

                st.download_button(
                    "Download Result JSON",
                    data=json.dumps(
                        result_data,
                        indent=2
                    ),
                    file_name="localization_result.json",
                    mime="application/json",
                )

        except Exception as e:
            st.error(
                f"Processing failed: {e}"
            )