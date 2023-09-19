from typing import Iterator, Tuple
from pkgs.modifiers.modifier import Modifier
from enum import Enum    
class PII_Type(str, Enum):
    phone = "PHONE_NUMBER"
    email = "EMAIL_ADDRESS"
    person = "PERSON"
    place = "LOCATION"
    time = "DATE_TIME"
    social = "NRP"
    ip = "IP_ADDRESS"
    card = "CREDIT_CARD"
    bank = "US_BANK_NUMBER"
    passport = "US_PASSPORT"
    ssn = "US_SSN"

#How do we identify which PII are the same?
class EntityResolution(str, Enum):
    equality = "EQUALITY"
    containment = "CONTAINMENT"
class Anonymizer(Modifier):
    """
    Modifier to anonymize any PII from text
    """

    def _find_pii_locations(self, text: str) -> Iterator[Tuple[int, int, str]]:
        """
        Find all locations of PII within text
        Returns iterator of (start_index, end_index, pii_type) tuples.
        """
        raise NotImplementedError("_find_pii_locations must be implemented")

    def _encrypt(self, raw: str) -> bytes:
        """
        Encrypt the inputted text 
        """
        raise NotImplementedError("_encrypt must be implemented")

    def _is_same_entity(self, pii_1: str, pii_2: str) -> bool:
        """
        Identifies whether two pieces of PII refer to the same entity.
        """
        return pii_1 == pii_2

    def _transform(self, text: str) -> str:
        pii_locations = sorted(self._find_pii_locations(text), key=lambda location: location[0])
        pii_to_token = {}
        cursor = i = 0
        anonymized_string = ""
        num_pii = len(pii_locations)

        while i < num_pii:
            start, end, pii_type = pii_locations[i]
            while i < num_pii - 1 and end > pii_locations[i+1][0] - 2 and pii_type == pii_locations[i+1][2]:
                i += 1
                end = pii_locations[i][1]
            pii = text[start:end]
            for other_pii in pii_to_token:
                if self._is_same_entity(pii, other_pii):
                    token = pii_to_token[other_pii]
                    break
            else:
                token = self._encrypt(pii).decode('utf-8')
                pii_to_token[pii] = token
            anonymized_string += text[cursor:start] + f"α{token}α"
            cursor = end
            i += 1
        return anonymized_string + text[cursor:]

    
class Deanonymizer(Modifier):
    """
    Modifier to de-anonymize a PII-anonymized text
    """

    def _decrypt(self, enc: str | bytes) -> str:
        """
        Decrypt the inputted encryption
        """
        raise NotImplementedError("_decrypt must be implemented")

    def _transform(self, text: str) -> str:
        cursor = 0
        raw_text = ""
        while True:
            next_token_start = text.find("α", cursor)
            if next_token_start == -1:
                break
            next_token_end = text.find("α", next_token_start + 1)
            assert next_token_end != -1, "malformed PSaLM output"
            raw_text += text[cursor:next_token_start] + self._decrypt(text[next_token_start + 1:next_token_end])
            cursor = next_token_end + 1
        return raw_text + text[cursor:]
