"""Easy grader: accuracy = (TP + TN) / N"""
from env.models import EnvState

_SCORE_MIN = 0.01
_SCORE_MAX = 0.99


def _clamp(score: float) -> float:
    """Ensure score is strictly between 0 and 1 (exclusive)."""
    return max(_SCORE_MIN, min(_SCORE_MAX, float(score)))


def easy_grader(state: EnvState) -> float:
    """Return accuracy over the episode history. Range (0.01, 0.99)."""
    if not state.history:
        return 0.1
    correct = sum(1 for e in state.history if e.get('correct', False))
    raw_score = correct / len(state.history)
    bounded = max(0.0, min(1.0, raw_score))
    return _clamp(0.1 + (0.8 * bounded))
