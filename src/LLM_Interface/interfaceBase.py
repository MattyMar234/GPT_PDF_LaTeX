from abc import ABC, abstractmethod
from typing import Any

import PIL
from google.generativeai.types import GenerateContentResponse

class LLMInterfaceBase(ABC):
    
    def __init__(self):
        pass
    
    @abstractmethod
    def chat(self, prompt: str, image: PIL.Image.Image | None = None, stream: bool=False) -> dict | GenerateContentResponse:
        pass