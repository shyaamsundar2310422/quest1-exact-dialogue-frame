def calculate_confidence(match_score, candidate_timestamp, refined_timestamp):
    """
    Calculate a simple confidence score from:
    - text matching quality
    - temporal refinement stability
    """

    text_score = max(0.0, min(100.0, float(match_score)))

    time_delta = abs(
        float(refined_timestamp) -
        float(candidate_timestamp)
    )

    # Small temporal adjustments indicate stable localization.
    if time_delta <= 0.25:
        temporal_score = 100.0
    elif time_delta <= 0.50:
        temporal_score = 90.0
    elif time_delta <= 1.00:
        temporal_score = 75.0
    else:
        temporal_score = 50.0

    confidence = (
        0.7 * text_score +
        0.3 * temporal_score
    )

    return round(confidence, 2)