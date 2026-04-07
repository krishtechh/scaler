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
    assert easy_grader(state) == 1.0


def test_easy_grader_none_correct():
    history = [_event(1, 'allow', correct=False), _event(0, 'block', correct=False)]
    state = make_state(history)
    assert easy_grader(state) == 0.0


def test_easy_grader_empty():
    assert easy_grader(make_state([])) == 0.0


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


def test_medium_grader_empty():
    assert medium_grader(make_state([])) == 0.0


def test_medium_grader_perfect():
    history = [
        _event(1, 'block', attack_type='obfuscated'),
        _event(0, 'allow'),
    ]
    state = make_state(history)
    score = medium_grader(state)
    assert score == 1.0


# ---- Hard grader tests ----

def test_hard_grader_perfect_recall():
    history = [
        _event(0, 'allow'),
        _event(0, 'allow'),
        _event(0, 'allow'),
        _event(1, 'block', attack_type='instruction_override'),
    ]
    state = make_state(history)
    score = hard_grader(state)
    assert 0.0 <= score <= 1.0
    # Perfect recall (detected all malicious) → score should be high
    assert score >= 0.5


def test_hard_grader_zero_recall():
    history = [
        _event(1, 'allow', correct=False, attack_type='role_reassignment'),
        _event(1, 'allow', correct=False, attack_type='role_reassignment'),
    ]
    state = make_state(history)
    score = hard_grader(state)
    assert score < 0.5


def test_hard_grader_empty():
    assert hard_grader(make_state([])) == 0.0
