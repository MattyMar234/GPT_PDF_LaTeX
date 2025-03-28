from LLM_Interface.interfaceBase import LLMInterfaceBase, MODEL_INFO
from LLM_Interface.geminiInterface import GoogleGeminiInterface
from LLM_Interface.ollamaInterface import OllamaInterface

import logging

class LLM_InterfaceFactory:
    
    @staticmethod
    def makeInterface(modelType: LLMInterfaceBase.Models | None, **kwargs) -> LLMInterfaceBase | None:
        if modelType is None:
            return None
        
        match modelType.value[MODEL_INFO.SERVICE]:
            
            case "google":
                logging.info(f"Creating GoogleGemini interface for {modelType.value[MODEL_INFO.MODEL_TYPE]}")
                return GoogleGeminiInterface(modelType)
            
            case "ollama":
                host = f'{kwargs["ollama_host"]}:{kwargs["ollama_port"]}'
                logging.info(f"Creating ollama interface for {modelType.value[MODEL_INFO.MODEL_TYPE]} listening on {host}")
                return OllamaInterface(
                    modelType, 
                    host = kwargs["ollama_host"], 
                    port = kwargs["ollama_port"],
                    timeout_s = kwargs["ollama_timeout"]
                )
     
            case _ :
                raise Exception("Unsupported Interface type")