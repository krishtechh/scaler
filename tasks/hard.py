"""Task selector for the Hard task.

Hard: multi-turn escalation sequences where early turns look benign and
later turns gradually reveal malicious intent.

Strategy: group prompts into sequences of 4 turns. Each sequence starts with
benign prompts and ends with a malicious one. This is deterministic given a seed.
"""
import random
from env.dataset import DF
from typing import List, Dict


def task_selector(seed: int = 42, length: int = 200) -> List[Dict]:
    """Build multi-turn escalation sequences from the dataset."""
    random.seed(seed)

    malicious = DF[DF['label'] == 1].to_dict(orient='records')
    benign = DF[DF['label'] == 0].to_dict(orient='records')

    # Shuffle deterministically
    random.shuffle(malicious)
    random.shuffle(benign)

    sequences: List[Dict] = []
    seq_len = 4  # turns per sequence
    m_idx, b_idx = 0, 0

    while len(sequences) < length:
        # 3 benign turns + 1 malicious escalation
        for _ in range(seq_len - 1):
            if b_idx >= len(benign):
                b_idx = 0
                random.shuffle(benign)
            record = dict(benign[b_idx])
            record['sequence_role'] = 'context'
            sequences.append(record)
            b_idx += 1

        if m_idx >= len(malicious):
            m_idx = 0
            random.shuffle(malicious)
        record = dict(malicious[m_idx])
        record['sequence_role'] = 'escalation'
        sequences.append(record)
        m_idx += 1

    return sequences[:length]
