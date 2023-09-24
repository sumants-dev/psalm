from typing import TypeVar
from pkgs import Node
from pkgs.models.pontus.base import ChatMessage
from pkgs.models import pydantic_openai

transform_types = (str, list, dict, Node)

T = TypeVar("T", *transform_types)


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
                if isinstance(data[key], transform_types):
                    data[key] = self.transform(data[key])
        elif isinstance(data, Node):
            data.content = self._transform(data.content)
            data.metadata = self.transform(data.metadata)
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
                    if isinstance(data[i], transform_types):
                        data[i] = self.transform(data[i])
        return data
