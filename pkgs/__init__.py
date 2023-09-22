import dataclasses
from typing import Dict, List


@dataclasses.dataclass()
class Node:
    content: str
    metadata: Dict[str, str]
    embedding: List[float] | None
