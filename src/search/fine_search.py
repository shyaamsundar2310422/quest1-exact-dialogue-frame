import wave
import cv2
import numpy as np


def load_audio(audio_path):
    with wave.open(audio_path, "rb") as wav:
        sample_rate = wav.getframerate()
        channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        frames = wav.readframes(wav.getnframes())

    if sample_width == 2:
        audio = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
    elif sample_width == 4:
        audio = np.frombuffer(frames, dtype=np.int32).astype(np.float32)
    else:
        raise ValueError("Unsupported WAV sample width.")

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)

    return audio, sample_rate


def rms_energy(audio):
    return np.sqrt(np.mean(audio ** 2) + 1e-8)


def refine_speech_onset(
    audio_path,
    candidate_time,
    search_before=0.5,
    search_after=0.3,
    window_ms=20,
    hop_ms=10,
):
    audio, sample_rate = load_audio(audio_path)

    window = max(1, int(sample_rate * window_ms / 1000))
    hop = max(1, int(sample_rate * hop_ms / 1000))

    start = max(
        0,
        int((candidate_time - search_before) * sample_rate)
    )

    end = min(
        len(audio),
        int((candidate_time + search_after) * sample_rate)
    )

    energies = []
    times = []

    for pos in range(start, end - window, hop):
        chunk = audio[pos:pos + window]

        energy = rms_energy(chunk)

        energies.append(energy)
        times.append(pos / sample_rate)

    if not energies:
        raise RuntimeError("No audio samples available.")

    energies = np.asarray(energies)
    times = np.asarray(times)

    # Estimate local background energy before the candidate.
    baseline_mask = times < candidate_time - 0.15

    if baseline_mask.any():
        baseline = np.median(energies[baseline_mask])
    else:
        baseline = np.median(energies)

    threshold = max(
        baseline * 1.8,
        np.percentile(energies, 60)
    )

    # Find first sustained rise close to the Whisper candidate.
    candidate_index = np.searchsorted(
        times,
        candidate_time
    )

    for i in range(
        max(0, candidate_index - int(0.5 / (hop_ms / 1000))),
        len(energies) - 3
    ):
        if times[i] < candidate_time - search_before:
            continue

        if times[i] > candidate_time + search_after:
            break

        sustained = energies[i:i + 3]

        if np.all(sustained > threshold):
            return float(times[i])

    # Fallback: keep Whisper's timestamp.
    return float(candidate_time)


def timestamp_to_frame(video_path, timestamp):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(
            f"Unable to open video: {video_path}"
        )

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    frame_number = round(timestamp * fps)

    frame_number = max(
        0,
        min(frame_number, total_frames - 1)
    )

    cap.set(
        cv2.CAP_PROP_POS_FRAMES,
        frame_number
    )

    success, frame = cap.read()

    cap.release()

    if not success:
        raise RuntimeError(
            f"Unable to read frame {frame_number}"
        )

    return frame_number, fps, frame