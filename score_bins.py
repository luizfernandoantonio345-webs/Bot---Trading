# score_bins.py

SCORE_BINS = [
    (70, 75),
    (76, 80),
    (81, 85),
    (86, 90)
]


def normalize_score(score):
    try:
        score = int(score)
    except (ValueError, TypeError):
        return None

    return max(0, min(100, score))


def get_score_bin(score):
    score = normalize_score(score)
    if score is None:
        return None

    for low, high in SCORE_BINS:
        if low <= score <= high:
            return f"{low}-{high}"

    return None
