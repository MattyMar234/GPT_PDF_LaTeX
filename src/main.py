#====================================================================#
#mie librerie 
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






    

            


# response = client.chat(
#     model=f"llama3.2",
#     messages=[{"role": "user", "content": f"ciaoo"}]
# )

# print(response)

class PDF_PAGE_DATA(Enum):
    TEXT = "text"
    WORDS_DATA = "words"
    IMAGES = "images"

# def proccessPage(document: Document) -> bool:
#     page_content = document.page_content
#     page_content = document.page
#     print(page_content)
    
    
# def extract_page_data(page_index: int) -> dict:
    
#     page_data: dict = {
#         PDF_PAGE_DATA.TEXT: None,
#         PDF_PAGE_DATA.WORDS_DATA: None,
#         PDF_PAGE_DATA.IMAGES: None
#     }
    
#     with pdfplumber.open(PDF_PATH) as pdf:
#         pdf_pages = pdf.pages
#         if page_index >= len(pdf_pages):
#             raise Exception("page number out of range.") 
         
#         page = pdf.pages[page_index]
#         page_data[PDF_PAGE_DATA.TEXT] = page.extract_text()
#         page_data[PDF_PAGE_DATA.WORDS_DATA] = page.extract_words()
#         page_data[PDF_PAGE_DATA.IMAGES] = page.images
        
#     return page_data
        
    
# def proccessPDF() -> None:
#     reader: PdfReader = PdfReader(PDF_PATH)
#     metadata = reader.metadata
#     page_number = len(reader.pages)
    
#     print(f"Lettura del file {PDF_PATH}")
#     print("📄 Metadati del PDF:")
#     print(f"- Titolo: {metadata.title}")
#     print(f"- Autore: {metadata.author}")
#     print(f"- Numero di pagine: {page_number}")
#     print("-" * 50)
    
#     laTex_data = {
#         "libraries" : {},
#         "contents" : {}
#     }
    
#     for i in range(page_number):
        
#         print(f"Analizzando pagina [{i+1}/{page_number}]", end='\r')
#         result = extract_page_data(i)
        
#         #print(result[PDF_PAGE_DATA.TEXT])
        
#         # response: ollama.ChatResponse = client.chat(
#         #     model=f"{MODEL.LLAMA32.value}",
#         #     messages=[{"role": "user", "content": f"Realizza un documento Latex utilizzando queste:\n{result}. \
#         #                Non commentare. Non devi modificare il contenuto informativo. \
#         #                Nel risultato voglio avere le stesse infromazioni presenti in {PDF_PAGE_DATA.TEXT.value}. \
#         #                Devi solo adattare in latex le informazioni che ti ho passato. \
#         #                 Utilizza esclusivamente le informazioni fornite nel testo seguente. Non aggiungere, modificare o interpretare ulteriormente i dati. \
#         #                 Rispondi solo in base a quanto specificato. {PDF_PAGE_DATA.WORDS_DATA.value} serve solo a capire come sono le varia parole. \
#         #                 {PDF_PAGE_DATA.WORDS_DATA.value} non deve comparie nel risultato finale. {PDF_PAGE_DATA.IMAGES.value} contiene le informazioni delle imamgini presenti"}]
#         # )
        
#         response: ollama.ChatResponse = client.chat(
#             model=f"{MODEL.LLAMA32.value}",
#             messages=[
#                 {
#                     "role": "user",
#                     "content": f"\
#                         Questo sono le parole presenti in una pagina di un PDF: {result[PDF_PAGE_DATA.TEXT]}.\
#                         Trasforma questa pagia del PDF in latex. Il latex deve essere compatibile con quello di Texify, intellij. Traduci in itliano.\
#                         Non commentare, non volgio riassunti e non modificare il contenuto informativo.\
#                         Il risultato deve essere un documento latex.\
#                         Rispondi solo in base a quanto specificato.\
#                         Non utilizzare caratteri strani.\
#                         Quando devi scrivere una formula inline utilizza $...$ . Altrimenti utilizza $$...$$ .\
#                         Attenzione alle parentesi in più\
#                         Fai attenzio a chiudere i blocchi. Non diemnticare di mettere $ , \\] o \\end{'{equation}'} alla fine delle formule/equazioni quando vengono utilizzati."
#                         #"QUando c'è da inserire un'imamgine, metti solo i tag di latex."
                    
#                 }
#             ]
#         )
        
#         #  Quando devi scrivere delle equaizoni o formule (non in linea) utilizza: \\begin{'{equation}'} ed \\end{'{equation}'}\
#         #                 Se i blocchi \\begin{'{equation}'} ed \\end{'{equation}'} contengono solo testo, non utilizzari. Ovvero non volgio blocchi equaizone con dentro delle parole\
        
#         content = response.message['content']
        
        
#         response: ollama.ChatResponse = client.chat(
#             model=f"{MODEL.LLAMA32.value}",
#             messages=[
#                 {
#                     "role": "user",
#                     "content": "Correggi eventuali errori, tipo i blocci equazione non fatti bene, \
#                         parentsi mancati }, caratteri strani o $ mancanti. \
#                         Le formule non possono iniziare \\[ e finire con $. Una formula che incomincia con \
#                         \\[ deve finire con \\]. Se una formual incomincia con $ allora deve finire con il $.    \
#                         Non volgio vedere, ad esempio, delle robe $\\begin{itemize}$...\\end{itemize}$ che non hanno senso. " +
#                         f"LaTex: {content}"
#                         #"QUando c'è da inserire un'imamgine, metti solo i tag di latex."
#                 }
#             ]
#         )
        
#         content = response.message['content']
        
 
#         for line in content.splitlines():
#             if line.startswith("\\usepackage"):
#                 line = line.split('%')[0]
                
#                 if laTex_data["libraries"].get(line) is None:
#                     continue
                
#                 laTex_data["libraries"][line] = True
            
        
#         start = content.find(r"\begin{document}")
#         end = content.find(r"\end{document}")
#         if start != -1 and end != -1:
#             document_content = content[start + len(r"\begin{document}") : end].strip()
#             laTex_data["contents"][i] = document_content
#         else:
#             laTex_data["contents"][i] = ""
    
#     #print(content)
    
#     print()
    
    
#     latex_string = r"""\documentclass[a4paper, 12pt]{article} %report
# %\documentclass[12pt]{article}
# %\usepackage[italian]{babel}
# %\usepackage[english]{babel}

# % Packages
# \usepackage[a4paper, top=2cm, bottom=2cm, inner=2cm, outer=2cm, headheight=1cm, headsep=1cm, footskip=1cm]{geometry}
# \usepackage{setspace} % Interlinea
# %\usepackage{mathptmx} % Times New Roman
# \usepackage[utf8]{inputenc}
# \usepackage{graphicx, wrapfig}
# %\usepackage{amsmath}
# \usepackage{float}
# \usepackage{multicol}
# %\usepackage[hidelinks]{hyperref}
# \usepackage{listings}
# \usepackage[dvipsnames]{xcolor}
# \usepackage{hyperref} % Gestisce gli URL e i collegamenti ipertestuali
# \usepackage{breakurl} % Permette di spezzare gli URL lunghi
# \usepackage{forest}
# \usepackage{tikz}
# \usetikzlibrary{trees}
# \usepackage{amsmath}
# \usepackage{amssymb}"""

#     # Scrittura del contenuto nel file
#     with open(OUTPUT, "w") as file:
        
#         file.write(latex_string)
        
#         for k in laTex_data["libraries"].keys():
#             file.write(k)
        
#         file.write("\n\n\\begin{document}\n\n")
        
#         for k in laTex_data["contents"].keys():
#             content = laTex_data["contents"][k]
#             file.write(content)
        
#         file.write("\n\n\\end{document}\n\n")
    
    
    
    
    
    

# def main2() -> None:
    
    
#     proccessPDF()
#     return
    
#     reader = PdfReader(PDF_PATH)
#     metadata = reader.metadata

#     print("📄 Metadati del PDF:")
#     print(f"Titolo: {metadata.title}")
#     print(f"Autore: {metadata.author}")
#     print(f"Numero di pagine: {len(reader.pages)}")
#     print("-" * 50)
    
#     with pdfplumber.open(PDF_PATH) as pdf:
#         for i, page in enumerate(pdf.pages):
#             print(f"📄 Analizzando pagina {i+1}...")

#             # Estrarre testo
#             text = page.extract_text()

#             # Identificare titoli (testo grande e in grassetto)
#             words = page.extract_words()
#             #titles = [w["text"] for w in words if float(w["size"]) > 10]  # Soglia per titoli

#             # Verificare presenza di immagini
#             images = page.images

#             # Mostrare i tag della pagina
#             print(f"📑 Pagina {i+1} - Tag rilevati:")
#             if words:
#                 #print(f"🔹 Titoli: {titles}")
#                 print(f"🔹 Titoli: {words}")
#             print("-" * 50)
#             if images:
#                 print(f"🖼️ Immagini trovate: {len(images)}")
#                 print(images)
#             print("-" * 50)
#             print(text)
#             print("-" * 50)
#             break
    
#     return
    
#     pdf_loader: PyPDFLoader = PyPDFLoader(PDF_PATH)
#     documents: List[Document] = pdf_loader.load()  
    
#     for i, doc in enumerate(documents):
#         print(f"{'*'*20}Processando pagina {i+1}{'*'*20}") 
#         proccessPage(doc)


 
 
# def remove_annotations(file_list: List[str], output_path: str | None = None) -> None:
#     doc = fitz.open(file_list[0])  # Apri il PDF
    
#     for i, file in enumerate(file_list):
#         print(f"[{i + 1}/{len(file_list)}] - processing: {file}")
        
#         doc = fitz.open(file)  # Apri il PDF
        
#         for j, page in enumerate(doc):  # Itera su tutte le pagine
#             print(f"page [{j+1}/{len(doc)}]", end='\r')
            
#             images = page.get_images(full=True)
#             for img in images:
#                 xref = img[0]
#                 # Rimuovi l'immagine usando l'indice di riferimento
#                 page.delete_image(xref)
                
            
#             # new_content = []  # Nuovo contenuto della pagina senza disegni
#             # for item in page.get_contents():  # Ottieni tutti gli oggetti della pagina
#             #     print(type(item), item)
#             #     xref = item[0]
#             #     cont = doc.xref_stream(xref)  # Estrai lo stream dei comandi grafici

#             #     if "re" in cont or "m" in cont or "l" in cont or "c" in cont:
#             #         # "re" = rettangoli, "m" = movimenti, "l" = linee, "c" = curve
#             #         continue  # Salta questo contenuto (rimuove disegni vettoriali)
#             #     new_content.append(cont)

#             # # Sostituisce il contenuto della pagina senza i disegni
#             # page.clean_contents()
#             # for content in new_content:
#             #     page.insert_text((0, 0), content)
            
#             drawings = page.get_drawings()  # Ottieni gli oggetti di disegno
#             # if drawings:
#             #     print(f"Pagina {page.number}: {len(drawings)} disegni trovati")
#             if not drawings:
#                 continue  # Nessun disegno, passa alla prossima pagina

#             annotations = page.annots()
#             if annotations:
#                 for annot in annotations:
#                     # Rimuovi l'annotazione
#                     page.delete_annot(annot)
            

#             page.clean_contents()  # Rimuove il contenuto della pagina mantenendo il testo e le immagini
            
            
            
            
#             # print(f"page [{j+1}/{len(doc)}]: {len(page.annots())}")
#             # for annot in page.annots():  # Itera su tutte le annotazioni
                
#             #     print(f"page [{j+1}/{len(doc)}]: {annot}")
                
#             #     page.delete_annot(annot)  # Rimuove l'annotazione

#         doc.save(output_path)  # Salva il PDF modificato
#         doc.close()
        
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
    
    
    pdfManager = PDF_Manager(AppData.OUTPUT_FOLDER)
    pdfManager.doOperation(operation=operation, inputFils=files, model_Interface=LLM_Interface)
    

    
    
    
    
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - [%(levelname)s]: %(message)s')
    
    #from LLM_Interface.geminiInterface import GoogleGeminiInterface
    
    # modelInterface = GoogleGeminiInterface(GoogleGeminiInterface.MODELS.GEMINI_2_FLASH)
    # modelInterface.chat(prompt="Explain how AI works in a few words")
    main()

