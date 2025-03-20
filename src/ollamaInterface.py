from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents.base import Document
import ollama

import logging


class ollamaInterface:
    
    _URL = "http://[IP]:[PORT]/api/chat"
    
    def __init__(self, model: str, host: str = "localhost", port: int = "11434",) -> None:
        #self._url = f"http://{host}:{port}/api/chat"
        self._client: ollama.Client =  ollama.Client(host=f"http://{host}:{port}")
        self._model:str = model
        self._role: str = ""
    
        
    def getRole(self) -> str:
        return self._role
    
    def setRole(self, value: str) -> None:
        assert isinstance(value, str)    
        self._role = value
    

    def chat(self, content: str) -> dict:
        try:
            response: ollama.ChatResponse = self._client.chat(
                model = f"{self._model}",
                messages = [
                    {
                        "role" : f"{self._role}",
                        "content": f"{content}"
                    }
                ]
            )
            
            #response.message['content']
            return response
            
        except Exception as e:
            logging.error(e)
            return None