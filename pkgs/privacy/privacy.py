from pkgs.modifiers.anonymity.anonymizer import Anonymizer, Deanonymizer
from pkgs.token_mapping.token_mapping import TokenMapper
from pkgs.token_mapping.inmemory_token_mapping import InMemoryTokenMapper


class Privacy:
    anoymizer: Anonymizer
    deanoymizer: Deanonymizer
    token_mapper: TokenMapper

    def __init__(
        self,
        anoymizer: Anonymizer,
        deanonimyzer: Deanonymizer,
        token_mapper: TokenMapper | None = None,
    ) -> None:
        self.anoymizer = anoymizer
        self.deanoymizer = deanonimyzer
        self.token_mapper = token_mapper or InMemoryTokenMapper()
