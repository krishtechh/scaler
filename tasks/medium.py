"""Task selector for the Medium task.

Medium: includes obfuscated attacks and paraphrases.
"""
from env.dataset import get_task_samples
from typing import List, Dict


def task_selector(seed: int = 42, length: int = 200) -> List[Dict]:
    return get_task_samples('medium', seed, length)
