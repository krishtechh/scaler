"""Medium grader: weighted F1 for the malicious class."""
from env.models import EnvState
from sklearn.metrics import f1_score


def medium_grader(state: EnvState) -> float:
    """Return weighted F1 score for the malicious class. Range (0, 1)."""
    if not state.history:
        return 0.1

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
        bounded = max(0.0, min(1.0, float(raw_score)))
        return 0.1 + (0.8 * bounded)

    score = f1_score(y_true, y_pred, pos_label=1, average='weighted', zero_division=0)
    bounded = max(0.0, min(1.0, float(score)))
    return 0.1 + (0.8 * bounded)
