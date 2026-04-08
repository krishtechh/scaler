"""Easy grader: accuracy = (TP + TN) / N"""
from env.models import EnvState

_SCORE_MIN = 0.0001
_SCORE_MAX = 0.9999


def _clamp(score: float) -> float:
    """Ensure score is strictly between 0 and 1 (exclusive)."""
    return max(_SCORE_MIN, min(_SCORE_MAX, float(score)))


def easy_grader(state: EnvState) -> float:
    """Return accuracy over the episode history. Range (0.0001, 0.9999)."""
    if not state.history:
        return 0.5
    correct = sum(1 for e in state.history if e.get('correct', False))
    raw_score = correct / len(state.history)
    return _clamp(raw_score)
