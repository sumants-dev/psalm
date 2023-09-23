import dataclasses
from typing import Dict, List
from datetime import datetime


@dataclasses.dataclass()
class Node:
    content: str
    metadata: Dict[str, str]
    embedding: List[float] | None = None
    created_at: datetime | None = None
