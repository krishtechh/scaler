"""Sklearn baseline agent.

Loads the pre-trained vectorizer + model from scaler/models/ and
classifies each prompt.
"""
import os
import joblib
from env.models import Action
from env.core import LLMSafeguardEnv

_MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
_VEC_PATH = os.path.join(_MODEL_DIR, 'vectorizer.pkl')
_MOD_PATH = os.path.join(_MODEL_DIR, 'model.pkl')

vectorizer = joblib.load(_VEC_PATH)
model = joblib.load(_MOD_PATH)


def predict(prompt: str, threshold: float = 0.5) -> Action:
    """Return block/allow action based on sklearn model probability."""
    X = vectorizer.transform([prompt])
    prob = model.predict_proba(X)[0][1]
    decision = 'block' if prob >= threshold else 'allow'
    return Action(decision=decision, confidence=float(prob))


def run_baseline(task: str = 'easy', seed: int = 42, episode_length: int = 200) -> dict:
    """Run the sklearn baseline over a full episode and return scores."""
    env = LLMSafeguardEnv(episode_length=episode_length)
    obs = env.reset(seed=seed, task=task)
    done = False
    total_reward = 0.0

    while not done:
        action = predict(obs.prompt)
        obs, reward, done, info = env.step(action)
        total_reward += reward.reward

    state = env.state()
    correct = sum(1 for e in state.history if e.get('correct', False))
    n = len(state.history) or 1
    return {
        'task': task,
        'seed': seed,
        'baseline': 'sklearn',
        'accuracy': round(correct / n, 4),
        'total_reward': round(total_reward, 4),
        'episode_length': len(state.history),
    }


if __name__ == '__main__':
    for task in ('easy', 'medium', 'hard'):
        result = run_baseline(task, seed=42, episode_length=50)
        print(result)
