import os


DEFAULT_REVIEW_THRESHOLD = 68.0


def get_review_threshold() -> float:
    raw_value = os.getenv(
        "SANCTIONS_REVIEW_THRESHOLD",
        str(DEFAULT_REVIEW_THRESHOLD)
    )

    try:
        threshold = float(raw_value)
    except ValueError:
        threshold = DEFAULT_REVIEW_THRESHOLD

    return max(0.0, min(99.0, threshold))