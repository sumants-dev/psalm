from typing import Dict, List, TypeVar
from pkgs import Node
from pkgs.models.pontus.base import ChatMessage
from pkgs.models import pydantic_openai

T = TypeVar("T")

class Modifier:
    """
    Modifiers transform strings to other strings
    Examples include
     - Sanitizing PII
     - Removing toxic substrings
    """

    def _transform(self, text: str) -> str:
        """
        Transform text to new text
        """
        return text

    def transform(self, data: T) -> T:
        if isinstance(data, str):
            data = self._transform(data)
        elif isinstance(data, dict):
            for key in data:
                if isinstance(data[key], (str, list, dict)):
                    data[key] = self.transform(data[key])
        elif isinstance(data, list):
            assert data
            if isinstance(data[0], Node):
                for node in data:
                    node.content = self._transform(node.content)
            elif isinstance(data[0], ChatMessage):
                for message in data:
                    message.content = self._transform(message.content)
            elif isinstance(data[0], pydantic_openai.ChatCompletionChoice):
                for choice in data:
                    assert isinstance(choice, pydantic_openai.ChatCompletionChoice)
                    choice.message.content = self._transform(choice.message.content)
            else:
                for i in range(len(data)):
                    if isinstance(data[i], (str, list, dict)):
                        data[i] = self.transform(data[i])
        return data
        


        
class MultiModifier(Modifier):
    def __init__(self, modifiers: List[Modifier]):
        self.modifiers = modifiers

    def _transform(self, text: str) -> str:
        for modifier in self.modifiers:
            text = modifier._transform(text)
        return text
    
    def transform(self, nodes: List[Node]):
        for modifier in self.modifiers:
            modifier.transform(nodes)
