from abc import ABC, abstractmethod
from enum import auto, Enum
from typing import Any, List

import PIL
from google.generativeai.types import GenerateContentResponse


class MODEL_INFO(Enum):
    MODEL_TYPE = auto()
    IMAGE = auto()
    MAX_TOKEN = auto()
    FILE = auto()
    SERVICE = auto()


class LLMInterfaceBase(ABC):
    
    class Models(Enum):
        
        GEMINI_2_FLASH = {MODEL_INFO.SERVICE: "google", MODEL_INFO.MODEL_TYPE: "gemini-2.0-flash", MODEL_INFO.IMAGE : False, MODEL_INFO.FILE : True, MODEL_INFO.MAX_TOKEN : 1048576}
        
        LLAMA32         = {MODEL_INFO.SERVICE: "ollama", MODEL_INFO.MODEL_TYPE: "llama3.2",       MODEL_INFO.IMAGE : False}
        LLAMA32B1       = {MODEL_INFO.SERVICE: "ollama", MODEL_INFO.MODEL_TYPE:"llama3.2:b1",     MODEL_INFO.IMAGE : False}
        DEEPSEEKR1_14B  = {MODEL_INFO.SERVICE: "ollama", MODEL_INFO.MODEL_TYPE:"deepseek-r1:14b", MODEL_INFO.IMAGE : False}
        GEMMA3_12B      = {MODEL_INFO.SERVICE: "ollama", MODEL_INFO.MODEL_TYPE:"gemma3:12b",      MODEL_INFO.IMAGE : False}
        LLAVA_7B        = {MODEL_INFO.SERVICE: "ollama", MODEL_INFO.MODEL_TYPE:"llava:7b",        MODEL_INFO.IMAGE : True}
        LAVA_13B        = {MODEL_INFO.SERVICE: "ollama", MODEL_INFO.MODEL_TYPE:"llava:13b",       MODEL_INFO.IMAGE : True}
        
        @classmethod
        def avaialableOption(cls) -> List[str]:
            return list(map(lambda c: c.value[MODEL_INFO.MODEL_TYPE], cls))
        
        @classmethod
        def toEnum(cls, value: str):
            for i in cls:
                if i.value[MODEL_INFO.MODEL_TYPE] == value:
                    return i
            return None
    
  
    def __init__(self):
        pass
    
    def modelName2Enum(name: str) -> Models | None:    
        return LLMInterfaceBase.Models.toEnum(name)
    
    @abstractmethod
    def chat(self, prompt: str, image: PIL.Image.Image | None = None, stream: bool=False) -> dict | GenerateContentResponse:
        pass
    
   
    def chat(self, prompt: str, file: list, stream: bool=False) -> dict | GenerateContentResponse:
        raise Exception("Not implemented")