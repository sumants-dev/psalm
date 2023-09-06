from presidio_analyzer import AnalyzerEngine
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from enum import Enum
from typing import List, Optional, Tuple, Union

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


class BaseAnonymizer(object):
    def anonymize(self, raw_text: str) -> str:
        raise NotImplementedError

    def deanonymize(self, anonymized_text: str) -> str:
        raise NotImplementedError
    
class DefaultAnonymizer(BaseAnonymizer):
    bs = AES.block_size

    def __init__(self, key: str, pii_types: List[PII_Type] = []):
        self.key = hashlib.sha256(key.encode()).digest()
        self.pii_types = [pii_type.value for pii_type in pii_types]
        self.iv = Random.new().read(self.bs)
        self.analyzer = AnalyzerEngine()

    def anonymize(self, raw_text: str) -> str:
        if self.pii_types:
            pii_likelihoods = self.analyzer.analyze(text=raw_text, language = "en", entities = self.pii_types)
        else:
            pii_likelihoods = self.analyzer.analyze(text=raw_text, language = "en")

        pii_locations = sorted(
            filter(lambda pii: pii.score >= 0.5, pii_likelihoods),
            key = lambda pii: pii.start
        )
        iv_mapping = {}
        cursor = i = 0
        anonymized_string = ""
        num_pii = len(pii_locations)

        while i < num_pii:
            start = pii_locations[i].start
            end = pii_locations[i].end
            while i < num_pii - 1 and end > pii_locations[i+1].start - 2:
                i += 1
                end = pii_locations[i].end
            pii = raw_text[start:end]
            for other_pii in iv_mapping:
                if other_pii in pii:
                    encrypted = self._encrypt(raw_text[start:end], iv_mapping[other_pii])
                    break
                if pii in other_pii:
                    encrypted = self._encrypt(raw_text[start:end], iv_mapping[other_pii])
                    iv_mapping[pii] = encrypted[1]
                    break
            else:
                encrypted = self._encrypt(raw_text[start:end])
                iv_mapping[pii] = encrypted[1]
            token = encrypted[0].decode('utf-8')
            anonymized_string += raw_text[cursor:start] + f"α{token}α"
            cursor = end
            i += 1
        return anonymized_string + raw_text[cursor:]

    def deanonymize(self, anonymized_text: str) -> str:
        cursor = 0
        raw_text = ""
        while True:
            next_token_start = anonymized_text.find("α", cursor)
            if next_token_start == -1:
                break
            next_token_end = anonymized_text.find("α", next_token_start + 1)
            assert next_token_end != -1, "malformed PSaLM output"
            raw_text += anonymized_text[cursor:next_token_start] + self._decrypt(anonymized_text[next_token_start + 1:next_token_end])
            cursor = next_token_end + 1
        return raw_text + anonymized_text[cursor:]


    def _encrypt(self, raw: str, iv: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        raw = self._pad(raw)
        iv = iv or Random.new().read(self.bs)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode())), iv

    def _decrypt(self, enc: Union[str, bytes]) -> str:
        enc = base64.b64decode(enc)
        iv = enc[:self.bs]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return DefaultAnonymizer._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


class Anoymizers(BaseAnonymizer):
    def __init__(self, anoymizers: List[BaseAnonymizer]) -> None:
        self.anoymizers = anoymizers

    def anonymize(self, raw_text: str) -> str:
        for anoymizer in self.anoymizers:
            raw_text = anoymizer.anonymize(raw_text)
        return raw_text

    def deanonymize(self, txt: str) -> str:
        for anoymizer in reversed(self.anoymizers):
            txt = anoymizer.deanonymize(txt)
        return txt



if __name__ == "__main__":
    text = "My phone number is 2125555555 and my email is abc@gmail.com and my name is Gonzales Gama and I live in Texas and I think Texas is the greatest place on earth"
    anonymizer = DefaultAnonymizer(key="AsnDnjkktOPMNrS=", pii_types = [PII_Type.phone, PII_Type.email, PII_Type.person, PII_Type.place])
    output = anonymizer.anonymize(text)
    print(output)
    print(anonymizer.deanonymize(output))