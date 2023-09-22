from pkgs.modifiers.modifier import Modifier
from spacy import load


class RemoveStopWords(Modifier):
    """
    Remove stop words from text to reduce token usage
    """

    def __init__(self):
        self.stop_words = load("en_core_web_lg").Defaults.stop_words

    def _transform(self, text: str) -> str:
        return " ".join(
            word.encode("ascii", "ignore").decode("utf-8")
            for word in text.split()
            if word and not word.isspace() and word.lower() not in self.stop_words
        )
