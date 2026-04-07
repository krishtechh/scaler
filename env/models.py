from pydantic import BaseModel
from typing import Literal, Optional, Dict, Any, List


class Action(BaseModel):
    decision: Literal["allow", "block", "defer", "sanitize"]
    confidence: Optional[float] = None
    metadata: Dict[str, Any] = {}


class Observation(BaseModel):
    prompt: str
    index: int
    remaining: int
    metadata: Dict[str, Any] = {}


class RewardModel(BaseModel):
    reward: float


class EnvState(BaseModel):
    index: int
    task_id: str
    seed: int
    history: List[Dict[str, Any]]
    config: Dict[str, Any]
