"""Unit tests for the LLMSafeguardEnv core."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from env.core import LLMSafeguardEnv, compute_reward
from env.models import Action


@pytest.fixture
def env():
    return LLMSafeguardEnv(episode_length=10)


def test_reset_returns_observation(env):
    obs = env.reset(seed=42, task='easy')
    assert obs.prompt != '' or obs.index == 0
    assert obs.index == 0
    assert obs.remaining >= 0


def test_reset_is_deterministic(env):
    obs1 = env.reset(seed=42, task='easy')
    obs2 = env.reset(seed=42, task='easy')
    assert obs1.prompt == obs2.prompt
    assert obs1.index == obs2.index


def test_step_advances_index(env):
    env.reset(seed=42, task='easy')
    action = Action(decision='block')
    obs, reward, done, info = env.step(action)
    assert env.state().index == 1


def test_step_returns_reward_model(env):
    env.reset(seed=42, task='easy')
    action = Action(decision='allow')
    obs, reward, done, info = env.step(action)
    assert isinstance(reward.reward, float)


def test_done_after_episode_length(env):
    env.reset(seed=42, task='easy', episode_length=5)
    done = False
    steps = 0
    while not done:
        _, _, done, _ = env.step(Action(decision='block'))
        steps += 1
    assert steps == 5


def test_state_is_reproducible(env):
    env.reset(seed=99, task='medium')
    for _ in range(3):
        env.step(Action(decision='block'))
    state = env.state()
    assert state.seed == 99
    assert state.task_id == 'medium'
    assert len(state.history) == 3


def test_compute_reward_malicious_block():
    r = compute_reward(Action(decision='block'), label=1, attack_type='prompt_extraction')
    assert r > 0


def test_compute_reward_malicious_allow():
    r = compute_reward(Action(decision='allow'), label=1, attack_type='prompt_extraction')
    assert r < 0


def test_compute_reward_benign_allow():
    r = compute_reward(Action(decision='allow'), label=0, attack_type='benign')
    assert r > 0


def test_compute_reward_benign_block():
    r = compute_reward(Action(decision='block'), label=0, attack_type='benign')
    assert r < 0


def test_step_before_reset_raises(env):
    with pytest.raises(RuntimeError):
        env.step(Action(decision='allow'))


def test_all_tasks_reset(env):
    for task in ('easy', 'medium', 'hard'):
        obs = env.reset(seed=42, task=task)
        assert obs.index == 0, f"Expected index=0 for task={task}"
