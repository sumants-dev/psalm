from pkgs.loaders.loader import Loader
from typing import List

from pkgs.modifiers.modifier import Modifier


class Population:
    def __init__(self, loader: Loader) -> None:
        self.loader = loader
