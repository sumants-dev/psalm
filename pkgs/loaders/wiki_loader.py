from pkgs.loaders.loader import Loader
import requests


class WikiLoader(Loader):
    """
    Loads articles from wikipedia using their titles
    """

    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts",
        "explaintext": True,
        "exsectionformat": "plain",
    }

    def _load(self, resource: str) -> str:
        response = requests.get(
            url=self.api_url, params={"titles": resource, **self.params}
        )
        return next(iter(response.json()["query"]["pages"].values()))["extract"]
