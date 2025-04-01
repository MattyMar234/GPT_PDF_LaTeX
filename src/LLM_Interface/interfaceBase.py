from abc import ABC, abstractmethod
from enum import auto, Enum
import logging
import threading
import time
from typing import Any, List

import PIL
from google.generativeai.types import GenerateContentResponse


class MODEL_INFO(Enum):
    MODEL_TYPE = auto()
    IMAGE = auto()
    MAX_TOKEN = auto()
    FILE = auto()
    SERVICE = auto()
    RPM = auto()
    RPD = auto()

class LLMInterfaceBase(ABC):
    
    class Models(Enum):
        
        GEMINI_2_FLASH = {
            MODEL_INFO.SERVICE: "google", 
            MODEL_INFO.MODEL_TYPE: "gemini-2.0-flash", 
            MODEL_INFO.IMAGE : False, 
            MODEL_INFO.FILE : True, 
            MODEL_INFO.RPM : 15,
            MODEL_INFO.RPD : 1500,
            MODEL_INFO.MAX_TOKEN : 1048576
        }
        
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
    
  
    def __init__(self, modelType: Models):
        assert isinstance(modelType, LLMInterfaceBase.Models)
        self._selectedModel = modelType
        self._lastRequest_time = time.time()
    
    def _sleepFor_RPM(self) -> None:
        value_RPM = self._selectedModel.value.get(MODEL_INFO.RPM) 
        if value_RPM is None: return

        value = (60/value_RPM) + 0.5        #il valore dello sleep
        requestTime = time.time()           #quando sto facendo questa richiesta
        dt = requestTime - self._lastRequest_time # il tempo trascorso dall'ultima richiesta

        #se il tempo che è passato dall'ultima richiesta è superiore al valore di attesa, esco.
        if dt >= value:
            return
        
        #dormo per la differenza
        sleep_value = max(value - dt, 0)
        logging.info(f"thread {threading.get_ident()} sleeping for {sleep_value:0.3f} s for RPM limit")
        time.sleep(sleep_value)
            
    
    def modelName2Enum(name: str) -> Models | None:    
        return LLMInterfaceBase.Models.toEnum(name)
    
    @abstractmethod
    def chat(self, prompt: str, image: PIL.Image.Image | None = None, stream: bool=False) -> dict | GenerateContentResponse:
        pass
    
   
    def chat(self, prompt: str, file: list, stream: bool=False) -> dict | GenerateContentResponse:
        raise Exception("Not implemented")