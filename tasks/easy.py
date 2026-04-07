"""Task selector for the Easy task.

Easy: clear malicious/benign prompts, no obfuscation.
"""
from env.dataset import get_task_samples
from typing import List, Dict


def task_selector(seed: int = 42, length: int = 200) -> List[Dict]:
    return get_task_samples('easy', seed, length)
