#====================================================================#
#mie librerie 
import time
from AppData import *
import AppData
from PDF_manager import PDF_Manager
from LLM_Interface.interfaceBase import LLMInterfaceBase
from LLM_Interface.InterfaceFactory import LLM_InterfaceFactory

# #====================================================================#
# #utile per operazioni di base come unire, dividere ed estrarre testo
# import PyPDF2
# from PyPDF2 import PdfReader

# #====================================================================#

# from pdf2image import convert_from_path
# import pdfplumber
# import fitz  # PyMuPDF

from enum import Enum, auto
from typing import List, Tuple
import requests
import argparse
import os
import logging





# PDF_PATH = "/app/inputs/ACbasics.pdf"
# OUTPUT = "./outputs/ACbasics.tex"
# URL = 'http://192.168.1.150:11434/api/chat'






    

        

class PDF_PAGE_DATA(Enum):
    TEXT = "text"
    WORDS_DATA = "words"
    IMAGES = "images"

        
def find_PDFs_in_a_folder(folderPath: str | None) -> List[str]:
    if folderPath is None or folderPath == "":
        return []
    
    out: List[str] = []
    
    for path in os.listdir(folderPath):
        if not os.path.isdir(path) and path.lower().endswith(".pdf"):
                out.append(os.path.join(folderPath, path))
        else:
            out.extend(find_PDFs_in_a_folder(path))           
    return sorted(out)


def makeFileList(sequenze) -> Tuple[bool, List[str]]:
    files: List[str] = []
    error: bool = False
    
    for item in sequenze:
        path: str = str(item)
        if not os.path.exists(item):
            print(f"Errore: Percorso '{item}' non trovato")
            error=True
            continue
        
        if os.path.isdir(path):
            files.extend(find_PDFs_in_a_folder(path))
        else:
            if path.split('.')[1].lower() == "pdf":
                files.append(path)
            else:
                print(f"Errore: File '{path}' non valido.")
                
    return (error, files)

def main() -> None:
    
    files: List[str] = []
    operation: PDF_Manager.OPERATION | None = None
    LLM_Interface: LLMInterfaceBase | None = None
    
  
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", choices=PDF_Manager.OPERATION.avaialableOption(), help="Operazione da eseguire")
    parser.add_argument("--files", nargs="+", help="Lista di file o cartelle contenenti PDF")
    parser.add_argument("--model", choices=LLMInterfaceBase.Models.avaialableOption(), type=str, help="Modello da utilizzare")
    parser.add_argument("--output", help="Percorso del file di output (predefinito: merged.pdf).")
    parser.add_argument("--pageindex", nargs="+", type=int)
    parser.add_argument("--ollama_timeout", type=int, default=40)
    parser.add_argument("--ollama_host", type=str, default="localhost")
    parser.add_argument("--ollama_port", type=int, default=11434)
    
    
    args = parser.parse_args()
    
    if not args.operation:
        print("Errore: tipo di operazione non specificata")
        return
    
    operation = PDF_Manager.OPERATION.toName(args.operation)
    
    if operation is None:
        print("Errore: Operazione \"args.operation\" sconosciuta")
        return
    
    errors, files = makeFileList(args.files)
    
    if errors:
        print("Operazione annullata: alcuni file non sono stati trovati")
        return
    
    if len(files) == 0:
        print("Errore: Nessun file PDF valido trovato.")
        return
    
    if args.model:
        LLM_Interface = LLM_InterfaceFactory.makeInterface(
            LLMInterfaceBase.modelName2Enum(args.model),
            ollama_timeout = args.ollama_timeout,
            ollama_host = args.ollama_host,
            ollama_port = args.ollama_port
        )
        
        if LLM_Interface is None:
            print(f"Errore: Modello '{args.model}' non trovato ")
    
    logging.info("files selected:")
    for f in files:
        logging.info(f"- {f}")

    time.sleep(2)
     
    outputFolder:str = AppData.OUTPUT_FOLDER if not args.output or not os.path.exists(args.output) else args.output
    
    pdfManager = PDF_Manager(outputFolder)
    pdfManager.doOperation(operation=operation, inputFils=files, model_Interface=LLM_Interface)
    #LLM_Interface.sleepFor_RPM()

    
    
    
    
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - [%(levelname)s]: %(message)s')
    main()

