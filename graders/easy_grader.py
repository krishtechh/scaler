"""Easy grader: accuracy = (TP + TN) / N"""
from env.models import EnvState


def easy_grader(state: EnvState) -> float:
    """Return accuracy over the episode history. Range (0, 1)."""
    if not state.history:
        return 0.1
    correct = sum(1 for e in state.history if e.get('correct', False))
    raw_score = correct / len(state.history)
    bounded = max(0.0, min(1.0, raw_score))
    return 0.1 + (0.8 * bounded)
