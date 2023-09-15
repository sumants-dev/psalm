from presidio_analyzer import AnalyzerEngine
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from enum import Enum
from typing import List, Tuple
from pkgs.modifiers.anonymity.anonymizer import Anonymizer, Deanonymizer

class PII_Type(Enum):
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
class EntityResolution(Enum):
    equality = "EQUALITY"
    containment = "CONTAINMENT"
    
class PresidioAnonymizer(Anonymizer):
    bs = AES.block_size

    def __init__(self, key: str, threshold: float, entity_resolution: EntityResolution, pii_types: List[PII_Type] = []):
        self.key = hashlib.sha256(key.encode()).digest()
        self.pii_types = [pii_type.value for pii_type in pii_types]
        assert threshold >= 0 and threshold <= 1
        self.threshold = threshold
        self.entity_resolution = entity_resolution
        self.analyzer = AnalyzerEngine()

    def _find_pii_locations(self, text: str) -> List[Tuple[int, int, str]]:
        if self.pii_types:
            pii_likelihoods = self.analyzer.analyze(text=text, language = "en", entities = self.pii_types)
        else:
            pii_likelihoods = self.analyzer.analyze(text=text, language = "en")
        
        return [(pii.start, pii.end, pii.entity_type) for pii in pii_likelihoods if pii.score >= self.threshold]
    
    def _pad(self, s: str) -> str:
        """
        Add padding to get the string to have a length divisible by self.bs
        """
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
    
    def _encrypt(self, raw: str) -> str | bytes:
        raw = self._pad(raw)
        iv = Random.new().read(self.bs)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))
    
    def _is_same_entity(self, pii_1: str, pii_2: str) -> bool:
        if self.entity_resolution == EntityResolution.equality:
            return pii_1 == pii_2
        else:
            return pii_1 in pii_2 or pii_2 in pii_1
        raise Exception("Invalid entity resolution algorithm")


class PresidioDeanonymizer(Deanonymizer):
    bs = AES.block_size

    def __init__(self, key: str):
        self.key = hashlib.sha256(key.encode()).digest()

    def _decrypt(self, enc: str | bytes) -> str:
        if isinstance(enc, str):
            enc = base64.b64decode(enc)
        iv = enc[:self.bs]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[self.bs:])).decode('utf-8')

    def _unpad(self, s):
        """
        Undo padding
        """
        return s[:-ord(s[len(s)-1:])]


if __name__ == "__main__":
    text = "My phone number is 2125555555 and my email is abc@gmail.com and my name is Gonzales Gama and I live in Texas and I think Texas is the greatest place on earth"
    key="AsnDnjkktOPMNrS="
    anonymizer = Anonymizer(key=key, pii_types = [PII_Type.phone, PII_Type.email, PII_Type.person, PII_Type.place])
    deanonymizer = Deanonymizer(key=key)
    output = anonymizer.transform(text)
    print(output)
    print(deanonymizer.transform(output))