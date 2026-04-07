"""Medium grader: weighted F1 for the malicious class."""
from env.models import EnvState
from sklearn.metrics import f1_score


def medium_grader(state: EnvState) -> float:
    """Return weighted F1 score for the malicious class. Range [0, 1]."""
    if not state.history:
        return 0.0

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
        return round(sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true), 6)

    score = f1_score(y_true, y_pred, pos_label=1, average='weighted', zero_division=0)
    return round(float(score), 6)
