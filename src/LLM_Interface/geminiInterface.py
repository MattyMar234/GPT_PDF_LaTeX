
    
#from google import genai
from typing import Any

import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.generativeai.types import GenerateContentResponse
from google.generativeai.types import ContentsType
from enum import Enum

from LLM_Interface.interfaceBase import LLMInterfaceBase, MODEL_INFO
import PIL
from PIL import Image


API = "AIzaSyDvDFuAeeixpHlwyoKX5vO8g6C11xwPAwg"
genai.configure(api_key=API)


class GoogleGeminiInterface(LLMInterfaceBase):
     
    def __init__(self, modelType: LLMInterfaceBase.Models) -> None:
        super().__init__(modelType)
        
        #client = genai.Client(api_key=API)
        self._model = GenerativeModel(modelType.value[MODEL_INFO.MODEL_TYPE])
        
    def chat(self, prompt: str, image: PIL.Image.Image | None = None, stream: bool=False) -> dict | GenerateContentResponse:
        assert isinstance(prompt, str)
        if image is None:
            return self._model.generate_content(prompt, stream=stream)
        
        return self._model.generate_content([prompt, image], stream=stream)