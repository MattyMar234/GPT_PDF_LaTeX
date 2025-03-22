from enum import Enum
from typing import List
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_core.documents.base import Document
import httpx
import ollama
import traceback
import logging


class OllamaInterface:
    
    class MODELS(Enum):
        LLAMA32 = {"model": "llama3.2", "image" : False}
        LLAMA32B1 = {"model":"llama3.2:b1", "image" : False}
        DEEPSEEKR1_14B = {"model":"deepseek-r1:14b", "image" : False}
        GEMMA3_12B = {"model":"gemma3:12b", "image" : False}
        LLAVA_7B = {"model":"llava:7b", "image" : True}
        
        @classmethod
        def avaialableOption(cls) -> List[str]:
            return list(map(lambda c: c.value["model"], cls))
        
        @classmethod
        def toName(cls, value: str):
            for i in cls:
                if i.value["model"] == value:
                    return i
            return None
    
    
    _URL = "http://[IP]:[PORT]/api/chat"
    
    def __init__(self, model: MODELS, host: str = "localhost", port: int = "11434", timeout_s: int = 1) -> None:
        #self._url = f"http://{host}:{port}/api/chat"
        self._client: ollama.Client =  ollama.Client(host=f"http://{host}:{port}", timeout = timeout_s)
        self._model: OllamaInterface.MODELS = model
        self._role: str = ""
    
        
    def getRole(self) -> str:
        return self._role
    
    def setRole(self, value: str) -> None:
        assert isinstance(value, str)    
        self._role = value
    

    def chat(self, content: str, image_base64: str | List[str] | None = None) -> dict:
        
        
        # with open("immagine.jpg", "rb") as f:
        #     image_base64 = base64.b64encode(f.read()).decode("utf-8")
        
        
        try:
            response = None
            
            messageDict = {
                #"role" : f"{self._role}",
                "role": "user",
                "content": f"{content}"
            }
            
            if image_base64 is not None:
                if isinstance(image_base64, list):
                    messageDict["images"] = image_base64
                    
                elif isinstance(image_base64, str):
                    messageDict["images"] = [image_base64]
            
            
            response: ollama.ChatResponse = self._client.chat(
                model = f"{self._model.value["model"]}",
                messages = [messageDict]
            )
            
            
            #response.message['content']
            return response
        
        except ConnectionError as e:
            logging.error(e)
            print("Server Ollama non trovato")
        
            
        except Exception as e:
            if isinstance(e, httpx.ReadTimeout):
                raise e 
            
            logging.error(e)
            #logging.error("Stack trace:", exc_info=True)
            return None