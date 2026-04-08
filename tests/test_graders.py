"""Unit tests for grader functions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from env.models import EnvState
from graders.easy_grader import easy_grader
from graders.medium_grader import medium_grader
from graders.hard_grader import hard_grader


def make_state(history):
    return EnvState(
        index=len(history),
        task_id='test',
        seed=42,
        history=history,
        config={},
    )


def _event(label, decision, correct=None, attack_type='benign'):
    if correct is None:
        predicted_malicious = decision in ('block', 'sanitize')
        correct = (predicted_malicious == (label == 1))
    return {
        'index': 0,
        'prompt': 'test prompt',
        'label': label,
        'attack_type': attack_type,
        'action': {'decision': decision, 'confidence': None, 'metadata': {}},
        'reward': 0.0,
        'correct': correct,
        'ts': 0.0,
    }


# ---- Easy grader tests ----

def test_easy_grader_all_correct():
    history = [_event(1, 'block'), _event(0, 'allow'), _event(1, 'block')]
    state = make_state(history)
    assert 0.99 < easy_grader(state) <= 0.9999


def test_easy_grader_none_correct():
    history = [_event(1, 'allow', correct=False), _event(0, 'block', correct=False)]
    state = make_state(history)
    assert 0.0001 <= easy_grader(state) < 0.01


def test_easy_grader_empty():
    state = make_state([])
    assert easy_grader(state) == 0.5  # default


def test_easy_grader_in_range():
    history = [_event(1, 'block'), _event(1, 'allow', correct=False), _event(0, 'allow')]
    state = make_state(history)
    score = easy_grader(state)
    assert 0.0 <= score <= 1.0


def test_easy_grader_deterministic():
    history = [_event(1, 'block'), _event(0, 'allow')]
    state = make_state(history)
    assert easy_grader(state) == easy_grader(state)


# ---- Medium grader tests ----

def test_medium_grader_in_range():
    history = [
        _event(1, 'block', attack_type='obfuscated'),
        _event(0, 'allow'),
        _event(1, 'allow', correct=False, attack_type='obfuscated'),
    ]
    state = make_state(history)
    score = medium_grader(state)
    assert 0.0 <= score <= 1.0


def test_medium_grader_perfect():
    history = [
        _event(1, 'block', attack_type='obfuscated'),
        _event(0, 'allow'),
    ]
    state = make_state(history)
    score = medium_grader(state)
    assert 0.99 < score <= 0.9999


def test_medium_grader_miss():
    history = [
        _event(1, 'allow', attack_type='obfuscated'),  # False Negative
        _event(0, 'allow'),                            # True Negative
    ]
    state = make_state(history)
    score = medium_grader(state)
    # y_true = [1, 0], y_pred = [0, 0]
    # F1 weighted is around 0.33
    assert score < 0.4


def test_medium_grader_empty():
    state = make_state([])
    assert medium_grader(state) == 0.5  # default


# ---- Hard grader tests ----

def test_hard_grader_perfect_recall():
    history = [
        _event(0, 'allow'),
        _event(1, 'block', attack_type='instruction_override'),  # Correct block on first malicious turn
    ]
    state = make_state(history)
    score = hard_grader(state)
    assert 0.99 < score <= 0.9999

def test_hard_grader_zero_recall():
    history = [
        _event(1, 'allow', correct=False, attack_type='role_reassignment'),
        _event(1, 'allow', correct=False, attack_type='role_reassignment'),
    ]
    state = make_state(history)
    score = hard_grader(state)
    assert 0.0001 <= score < 0.01

def test_hard_grader_empty():
    state = make_state([])
    assert hard_grader(state) == 0.5  # default
