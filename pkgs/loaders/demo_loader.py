from typing import Dict, Tuple
from pkgs.loaders.loader import Loader, LoaderData


class DemoLoader(Loader):
    DEMO_DATA = {
        "resource1": "Demo text",
        "resource2": "Demo text",
        "resource3": "Demo text",
    }

    def _load(self, resource: str) -> LoaderData:
        return LoaderData(
            metadata={"doc": resource}, text=DemoLoader.DEMO_DATA[resource]
        )

    def bulk_load(self) -> Dict[str, LoaderData]:
        return {resource: self._load(resource) for resource in DemoLoader.DEMO_DATA}
