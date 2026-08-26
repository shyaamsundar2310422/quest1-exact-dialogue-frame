from rapidfuzz.fuzz import ratio


def normalize(text):
    return " ".join(text.lower().strip().split())


def find_dialogue(result, target, threshold=70):
    target_normalized = normalize(target)

    best_match = None
    best_score = 0

    for segment in result.get("segments", []):
        text = normalize(segment.get("text", ""))

        score = ratio(target_normalized, text)

        if score > best_score:
            best_score = score
            best_match = segment

    if best_match is None or best_score < threshold:
        return None

    words = best_match.get("words", [])

    return {
        "text": best_match.get("text", "").strip(),
        "score": best_score,
        "segment_start": best_match.get("start"),
        "segment_end": best_match.get("end"),
        "words": words,
    }