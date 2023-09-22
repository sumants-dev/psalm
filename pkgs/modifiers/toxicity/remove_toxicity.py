from profanity_check import predict
from pkgs.modifiers.modifier import Modifier


def check_toxicity(text: str) -> bool:
    return predict([text])[0] > 0.5


class RemoveToxicity(Modifier):
    default_response = (
        "This text used to contain offensive material, and was thus purged"
    )

    def __init__(self, threshold: float):
        assert threshold >= 0 and threshold <= 1
        self.threshold = threshold

    def _transform(self, text: str) -> str:
        return text if predict([text])[0] > self.threshold else self.default_response
