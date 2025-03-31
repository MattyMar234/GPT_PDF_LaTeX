
    
#from google import genai
import time
from typing import Any

import google.generativeai as genai
from google.generativeai import GenerativeModel
from google.generativeai.types import GenerateContentResponse
from google.generativeai.types import ContentsType
from enum import Enum
import threading

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
        self._lock = threading.Lock()


    def chat(self, prompt: str, image: PIL.Image.Image | None = None, stream: bool=False) -> dict | GenerateContentResponse:
        assert isinstance(prompt, str)
        assert isinstance(image, PIL.Image.Image | None )
        
        with self._lock:
            self._sleepFor_RPM()
            
            if image is None:
                return self._model.generate_content(prompt, stream=stream)
            
            result = self._model.generate_content([prompt, image], stream=stream)

            self._lastRequest_time = time.time()
            return result