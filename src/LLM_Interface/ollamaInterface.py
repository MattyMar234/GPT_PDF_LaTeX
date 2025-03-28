from enum import Enum
from typing import List
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_core.documents.base import Document
import httpx
import ollama
import traceback
import logging

from LLM_Interface.interfaceBase import LLMInterfaceBase, MODEL_INFO


class OllamaInterface(LLMInterfaceBase):
    

    _URL = "http://[IP]:[PORT]/api/chat"
    
    def __init__(self, model: LLMInterfaceBase.Models, host: str = "localhost", port: int | str = 11434, timeout_s: int = 1) -> None:
        assert isinstance(host, str)
        assert isinstance(port, str) or isinstance(port, int)
        assert isinstance(timeout_s, int)
        
        #self._url = f"http://{host}:{port}/api/chat"
        self._client: ollama.Client =  ollama.Client(host=f"http://{host}:{port}", timeout = timeout_s)
        self._model: OllamaInterface.MODELS = model.value[MODEL_INFO.MODEL_TYPE]
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