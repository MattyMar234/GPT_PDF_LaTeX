#====================================================================#
#mie librerie 
import re
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
from typing import Dict, List, Tuple
import requests
import argparse
import os
import logging




# Pattern per il formato di un file (opzionale) e le specifiche di pagine
FILE_PATTERN = r'^(?:([^:]+):)?(.+)$'

# Pattern per la specifica di una singola pagina:
# - Numero singolo (es. "1", "42")
# - Range (es. "1-5")
# - Asterisco ("*") per tutte le pagine
# - Numero seguito da asterisco (es. "2*") per "dalla pagina n alla fine"
PAGE_SPEC_PATTERN = r'^(\d+|\d+-\d+|\*|\d+\*)$'





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
    #print(os.listdir(folderPath))
    
    for item in os.listdir(folderPath):
        path = os.path.join(folderPath, item)
    
        if not os.path.isdir(path) and path.lower().endswith(".pdf"):
            out.append(os.path.join(folderPath, path))
        else:
            out.extend(find_PDFs_in_a_folder(path))           
    return out


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

def validate_page_spec_format(page_specs: List[str]) -> Dict[str, str] | None:
    """
    Verifica che le specifiche delle pagine rispettino il formato richiesto.
    
    Args:
        page_specs (list): Lista di stringhe nel formato 'file:page_spec' o solo 'page_spec'.
    
    Returns:
        bool: True se tutte le specifiche sono valide, False altrimenti.
        
    Raises:
        ValueError: Se una specifica non è valida, con il messaggio di errore.
    """
    
    global FILE_PATTERN
    global PAGE_SPEC_PATTERN
    
    file_data: Dict[str, str] = {}
    
    
    for spec in page_specs:
        # Controlla il formato complessivo (file:pages o solo pages)
        file_match = re.match(FILE_PATTERN, spec)
        if not file_match:
            raise ValueError(f"Formato non valido per la specifica: '{spec}'")
        
        file_name = spec.split(':')[0]              #nome del file
        page_part = file_match.group(2)             # Estrae la parte relativa alle pagine
        page_specs_parts = page_part.split(',')     # Suddivide le specifiche di pagina separate da virgole
        
        for page_spec in page_specs_parts:
            page_spec = page_spec.strip()
            if not re.match(PAGE_SPEC_PATTERN, page_spec):
                raise ValueError(f"Formato non valido per la specifica di pagina: '{page_spec}' in '{spec}'")
    
        file_data[file_name] = page_part
    return file_data



def parse_page_specifications(page_specs: str, total_pages: int = -1) -> List[int]:
    assert total_pages >= 0
    
    if total_pages == 0:
        return []
    
    elements: List[str] = page_specs.split(',')
    result: List[int] = []
    
    for part in elements:
        part = part.replace('\t', '').replace(' ', '')

        # Gestisci "*" (tutte le pagine)
        if  part == "*":
            result.extend(range(1, total_pages + 1))
            break
        
        # Gestisci "n*" (dalla pagina n alla fine)
        elif part.endswith("*") and part[:-1].isdigit():
            start_page = int(part[:-1])
            result.extend(range(start_page, total_pages + 1))
               
        # Gestisci range "n-m"
        elif "-" in part:
            start, end = part.split("-")
            start, end = int(start), int(end)
            result.extend(range(start, end + 1))
            
        # Gestisci singole pagine
        elif part.isdigit():
            result.append(int(part))
            
        else:
            raise ValueError(f"Value '{part}' not reconized")
     
    return sorted(list(set(result)))


def get_page_sequences(files_page_dict: Dict[str, str]):
    result: Dict[str, List[int]] = {}
    
    for f_keys in files_page_dict.keys():
        result[f_keys] = parse_page_specifications(files_page_dict[f_keys], 30)
    
    return result



def main() -> None:
    
    files: List[str] = []
    operation: PDF_Manager.OPERATION | None = None
    LLM_Interface: LLMInterfaceBase | None = None
    files_page_list: Dict[str, List[int]] | None = None
    
  
    parser = argparse.ArgumentParser()
    parser.add_argument("--operation", choices=PDF_Manager.OPERATION.avaialableOption(), help="Operazione da eseguire")
    parser.add_argument("--files", nargs="+", help="Lista di file o cartelle contenenti PDF")
    parser.add_argument("--model", choices=LLMInterfaceBase.Models.avaialableOption(), type=str, help="Modello da utilizzare")
    parser.add_argument("--output", help="Percorso del file di output (predefinito: merged.pdf).")
    parser.add_argument("--pages", nargs="+", type=str, help="Specifiche pagine per ogni file. Formato: 'file1:1,3,5-7,* file2:2*,10-12'. Usa '*' per tutte le pagine e 'n*' per indicare dalla pagina n fino alla fine.")
    parser.add_argument("--ollama_timeout", type=int, default=40)
    parser.add_argument("--ollama_host", type=str, default="localhost")
    parser.add_argument("--ollama_port", type=int, default=11434)
    
    
    args = parser.parse_args()
    
    if args.pages:
        try:
            files_page_dict: Dict[str, str] = validate_page_spec_format(args.pages)
            files_page_list = get_page_sequences(files_page_dict)

            print(files_page_list)
            return
    
        except ValueError as e:
            logging.error(f"Errore: {e}")

    
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
     
    outputFolder:str = args.output if args.output  else AppData.OUTPUT_FOLDER
    logging.info('-'*100)
    logging.info(f"Output Folder selected: {outputFolder}")
   
    if not os.path.exists(outputFolder):
        logging.error(f"Folder {outputFolder} not found")
        logging.info(f"Making folder {outputFolder}")
        os.makedirs(args.output)
    else:
        logging.info(f"Folder {outputFolder} found")

    logging.info('-'*100)
    time.sleep(1.5)        
    
    
    
    
    
    pdfManager = PDF_Manager(outputFolder)
    pdfManager.doOperation(operation=operation, inputFils=files, model_Interface=LLM_Interface)
    #LLM_Interface.sleepFor_RPM()

    
    
    
    
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - [%(levelname)s]: %(message)s')
    main()

