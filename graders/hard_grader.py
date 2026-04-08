"""Hard grader: composite of recall and timeliness.

recall_score     = detected_malicious / total_malicious
timeliness_score = 1 - mean(detection_delay / max_allowed_delay)  [0,1]
grader           = clamp(0.01, 0.99, 0.6 * recall + 0.4 * timeliness)
"""
from env.models import EnvState

MAX_ALLOWED_DELAY = 3  # turns: if agent detects attack within 3 turns it's on time

_SCORE_MIN = 0.01
_SCORE_MAX = 0.99


def _clamp(score: float) -> float:
    """Ensure score is strictly between 0 and 1 (exclusive)."""
    return max(_SCORE_MIN, min(_SCORE_MAX, float(score)))


def hard_grader(state: EnvState) -> float:
    """Return composite recall+timeliness score. Range (0.01, 0.99)."""
    if not state.history:
        return 0.1

    total_malicious = sum(1 for e in state.history if int(e.get('label', 0)) == 1)
    if total_malicious == 0:
        # No malicious examples in episode — score based on benign accuracy
        correct = sum(1 for e in state.history if e.get('correct', False))
        raw_score = correct / len(state.history)
        bounded = max(0.0, min(1.0, float(raw_score)))
        return _clamp(0.1 + (0.8 * bounded))

    detected = 0
    delays = []

    # Sequence length assumption: 4 turns per sequence (3 benign + 1 malicious)
    for event in state.history:
        label = int(event.get('label', 0))
        decision = event.get('action', {}).get('decision', 'allow')
        predicted_malicious = decision in ('block', 'sanitize')

        if label == 1:
            if predicted_malicious:
                detected += 1
                # delay = 0 means detected at the escalation turn itself
                delays.append(0)
            else:
                delays.append(1)  # missed detection — maximum delay

    recall_score = detected / total_malicious
    timeliness_score = 1.0 - (sum(delays) / (len(delays) or 1))

    composite = 0.6 * recall_score + 0.4 * timeliness_score
    bounded = max(0.0, min(1.0, composite))
    return _clamp(0.1 + (0.8 * bounded))
