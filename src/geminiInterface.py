API = "AIzaSyDvDFuAeeixpHlwyoKX5vO8g6C11xwPAwg"
    
#from google import genai
import google.generativeai as genai
from google.generativeai import GenerativeModel
from enum import Enum

#client = genai.Client(api_key=API)

genai.configure(api_key=API)


class GoogleGeminiInterface:
    
    class MODELS(Enum):
        GEMINI_2_FLASH = {"model": "gemini-2.0-flash", "image" : False}
        
        
    def __init__(self, modelType: MODELS, API: str) -> None:
        assert isinstance(modelType, GoogleGeminiInterface.MODELS)
        assert isinstance(API, str)
        
        self._model = GenerativeModel(modelType.value)
        
    def chat(self, prompt: str) -> None:
        response = self._model.generate_content(prompt)