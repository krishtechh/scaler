"""Easy grader: accuracy = (TP + TN) / N"""
from env.models import EnvState


def easy_grader(state: EnvState) -> float:
    """Return accuracy over the episode history. Range [0, 1]."""
    if not state.history:
        return 0.0
    correct = sum(1 for e in state.history if e.get('correct', False))
    return round(correct / len(state.history), 6)
