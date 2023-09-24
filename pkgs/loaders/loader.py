from typing import Dict, Tuple
from typing_extensions import TypedDict


class LoaderData(TypedDict):
    metadata: Dict[str, str]
    text: str


class Loader:
    """
    Loads data from various sources into context
    """

    def _load(self, resource: str) -> str:
        raise NotImplementedError("_load must be implemented")

    def load(self, resource: str, name: str | None = None) -> LoaderData:
        text = self._load(resource)
        metadata = {"doc": name or resource}
        return LoaderData(metadata=metadata, text=text)

    def bulk_load(self) -> Dict[str, LoaderData]:
        raise NotImplementedError("bulk_load must be implemented")
