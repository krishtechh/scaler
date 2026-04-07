import os
import pandas as pd
import random
from typing import List, Dict

# Resolve path relative to this package so it works from any CWD
_PKGD_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'data', 'prompts.csv'))
# Fallback for local development or simple Docker environments
_CWD_PATH = os.path.normpath(os.path.join(os.getcwd(), 'data', 'prompts.csv'))

_DATA_PATH = _PKGD_PATH if os.path.exists(_PKGD_PATH) else _CWD_PATH

try:
    DF = pd.read_csv(_DATA_PATH)
    # Normalise column names to lower-case, strip whitespace
    DF.columns = [c.strip().lower() for c in DF.columns]
    # Ensure 'attack_type' column exists; fall back to 'type' or 'category'
    if 'attack_type' not in DF.columns:
        for alt in ('type', 'category', 'attack type'):
            if alt in DF.columns:
                DF = DF.rename(columns={alt: 'attack_type'})
                break
        else:
            DF['attack_type'] = 'unknown'
    # Ensure 'label' column: 1 = malicious, 0 = benign
    if 'label' not in DF.columns:
        for alt in ('is_malicious', 'malicious', 'is_attack'):
            if alt in DF.columns:
                DF = DF.rename(columns={alt: 'label'})
                break
        else:
            DF['label'] = 0
    DF['label'] = DF['label'].astype(int)
    # Ensure 'prompt' column exists
    if 'prompt' not in DF.columns:
        for alt in ('text', 'input', 'content'):
            if alt in DF.columns:
                DF = DF.rename(columns={alt: 'prompt'})
                break
except Exception as e:
    import warnings
    warnings.warn(f"Could not load prompts.csv: {e}. Using empty DataFrame.")
    DF = pd.DataFrame(columns=['prompt', 'label', 'attack_type'])


def get_task_samples(task: str, seed: int, length: int) -> List[Dict]:
    """Return a deterministic list of sample dicts for the given task."""
    random.seed(seed)

    at = DF['attack_type'].astype(str)

    if task == 'easy':
        # Only clear attacks (no obfuscation) and benign prompts
        subset = DF[~at.str.contains('obfuscated', case=False, na=False)]
    elif task == 'medium':
        # Obfuscated attacks + constraint bypass + benign
        mask = (
            at.str.contains('obfuscated', case=False, na=False) |
            at.str.contains('constraint_bypass', case=False, na=False) |
            (DF['label'] == 0)
        )
        subset = DF[mask]
    else:
        # Hard: full dataset (multi-turn sequences built in tasks/hard.py)
        subset = DF

    if len(subset) == 0:
        subset = DF  # graceful fallback

    records = subset.sample(frac=1, random_state=seed).to_dict(orient='records')
    # Pad if dataset is smaller than requested length
    while len(records) < length:
        records = records + records
    return records[:length]
