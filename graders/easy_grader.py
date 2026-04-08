"""Easy grader: accuracy = (TP + TN) / N"""
from env.models import EnvState


def easy_grader(state: EnvState) -> float:
    """Return accuracy over the episode history. Range (0, 1)."""
    if not state.history:
        return 0.001
    correct = sum(1 for e in state.history if e.get('correct', False))
    raw_score = correct / len(state.history)
    return max(0.001, min(0.999, raw_score))
