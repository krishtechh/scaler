"""Medium grader: weighted F1 for the malicious class."""
from env.models import EnvState
from sklearn.metrics import f1_score

_SCORE_MIN = 0.0001
_SCORE_MAX = 0.9999


def _clamp(score: float) -> float:
    """Ensure score is strictly between 0 and 1 (exclusive)."""
    return max(_SCORE_MIN, min(_SCORE_MAX, float(score)))


def medium_grader(state: EnvState) -> float:
    """Return weighted F1 for malicious class. Range (0.0001, 0.9999)."""
    if not state.history:
        return 0.5

    y_true = []
    y_pred = []

    for event in state.history:
        label = int(event.get('label', 0))
        decision = event.get('action', {}).get('decision', 'allow')
        predicted = 1 if decision in ('block', 'sanitize') else 0
        y_true.append(label)
        y_pred.append(predicted)

    if len(set(y_true)) < 2:
        # Only one class present — fall back to accuracy
        raw_score = sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true)
        return _clamp(raw_score)

    score = f1_score(y_true, y_pred, pos_label=1, average='weighted', zero_division=0)
    return _clamp(score)
