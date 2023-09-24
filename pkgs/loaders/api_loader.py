from pkgs.loaders.loader import Loader, LoaderData
from typing import Dict
from requests import auth as RequestAuth
import requests


class ApiLoader(Loader):
    def __init__(
        self,
        endpoint: str,
        bulk_endpoint: str,
        auth: RequestAuth.HTTPBasicAuth,
        queries: Dict[str, str] = {},
        method: str = "GET",
    ) -> None:
        self.endpoint = endpoint
        self.bulk_endpoint = bulk_endpoint
        self.auth = auth
        self.queries = queries
        self.method = method

    def _load(self, resource: str) -> LoaderData:
        if self.method == "GET":
            response = requests.get(
                url=self.endpoint,
                params={"resource": resource, **self.queries},
                auth=self.auth,
            )

            return LoaderData(text=response.json()["text"], metadata={"doc": resource})
        else:
            raise NotImplementedError("Only GET method is supported")

    def bulk_load(self) -> Dict[str, LoaderData]:
        if self.method == "GET":
            response = requests.get(
                url=self.endpoint,
                params={**self.queries},
                auth=self.auth,
            )

            return response.json()
        else:
            raise NotImplementedError("Only GET method is supported")
