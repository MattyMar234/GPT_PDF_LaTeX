
    
#from google import genai
from typing import Any

import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.generativeai.types import GenerateContentResponse
from google.generativeai.types import ContentsType
from enum import Enum

from LLM_Interface.interfaceBase import LLMInterfaceBase
import PIL
from PIL import Image


API = "AIzaSyDvDFuAeeixpHlwyoKX5vO8g6C11xwPAwg"
genai.configure(api_key=API)


class GoogleGeminiInterface(LLMInterfaceBase):
    
    class MODELS(Enum):
        GEMINI_2_FLASH = {"model": "gemini-2.0-flash", "image" : False, "max_token" : 1048576}
        
        
    def __init__(self, modelType: MODELS) -> None:
        assert isinstance(modelType, GoogleGeminiInterface.MODELS)
        
        super().__init__()
        
        #client = genai.Client(api_key=API)
        self._model = GenerativeModel(modelType.value["model"])
        
    def chat(self, prompt: str, image: PIL.Image.Image | None = None, stream: bool=False) -> dict | GenerateContentResponse:
        assert isinstance(prompt, str)
        if image is None:
            return self._model.generate_content(prompt, stream=stream)
        
    
        return self._model.generate_content([prompt, image], stream=stream)