from typing import Dict, Tuple


class Loader:
    """
    Loads data from various sources into context
    """

    def _load(self, resource: str) -> str:
        raise NotImplementedError("_load must be implemented")

    def load(self, resource: str, name: str | None = None) -> Tuple[Dict, str]:
        text = self._load(resource)
        metadata = {"doc": name or resource}
        return metadata, text
