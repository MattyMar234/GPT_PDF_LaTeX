from typing import Final, List, Tuple
from datetime import datetime
from enum import Enum
from PIL import Image
import logging
import base64
import time
import os
import io
import re
import PyPDF2
import fitz
import httpx

from LLM_Interface.ollamaInterface import OllamaInterface
from LLM_Interface.interfaceBase import LLMInterfaceBase
from LLM_Interface.geminiInterface import GoogleGeminiInterface
    
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue


DEFAULT_PROMPT: Final[str] = """Using LaTeX syntax, convert the text recognised in the image into LaTeX format for output. You must do:
1. output the same language as the one that uses the recognised image, for example, for fields recognised in English, the output must be in English.
2. don't interpret the text which is not related to the output, and output the content in the image directly. For example, it is strictly forbidden to output examples like ``Here is the LaTeX text I generated based on the content of the image:'' Instead, you should output LaTeX code directly.
3. Content should not be included in ```latex ```, paragraph formulas should be in the form of $$ $$, in-line formulas should be in the form of $ $$, long straight lines should be ignored, and page numbers should be ignored.
Again, do not interpret text that is not relevant to the output, and output the content in the image directly.
In each page you could possibly find a title, so use section or subsection etc.
"""

DEFAULT_PROMPT_v2: Final[str] = """Usando la sintassi LaTeX, converti il testo riconosciuto nell'immagine in formato LaTeX per l'output. Devi fare quanto segue:  
1. L'output deve essere in lingua italiana.  
2. Non interpretare il testo che non è pertinente all'output e restituisci direttamente il contenuto presente nell'immagine. Ad esempio, è severamente vietato fornire introduzioni come ``Ecco il testo LaTeX che ho generato in base al contenuto dell'immagine:''; invece, devi restituire direttamente il codice LaTeX.  
3. Il contenuto non deve essere incluso tra ```latex ```, le formule nei paragrafi devono essere scritte nella forma $$ $$, le formule in linea nella forma $ $; le linee lunghe devono essere ignorate, così come i numeri di pagina.  
4. Evita caratteri Unicode e caratteri speciali, utilizzando invece i comandi LaTeX.  
5. Il contenuto latex deve essere dentro ad un blocco di codice.
Ancora una volta, non interpretare il testo che non è pertinente all'output e restituisci direttamente il contenuto dell'immagine.  
In ogni pagina potresti trovare un titolo, quindi utilizza `\section` o `\subsection`, ecc."""  


DEFAULT_RECT_PROMPT: Final[str] = """Areas are marked in the image with a red box and a name (%s) DO NOT CHANGE THE %s. If the regions are tables or images, use 
\\begin{center}
    	\\includegraphics[width=0.5\\linewidth,trim={0 0 0 0},clip]{%s} %trim={<left> <lower> <right> <upper>}
\\end{center}
form to insert into the output, otherwise output the text content directly. You could also use tikz if possible, but prefer images if the tikz is complex.
If instead the image is taking, for example the title, text and the correct part that should be the image, you could use the trim option in the includegraphics to remove the unwanted part (as it could be already present in the text version).
"""
DEFAULT_ROLE_PROMPT: Final[str] = """You are a PDF document parser that outputs the content of images using latex syntax. Remember to always use the latex syntax.
"""


LATEX_DOCUMENT_DATA: Final[str] = r"""
\documentclass[12pt]{article}
%\usepackage[italian]{babel}
%\usepackage[english]{babel}

% Packages
\usepackage[a4paper, top=2cm, bottom=2cm, inner=2cm, outer=2cm, headheight=1cm, headsep=1cm, footskip=1cm]{geometry}
\usepackage{setspace} % Interlinea

\usepackage[utf8]{inputenc}
\usepackage{graphicx, wrapfig}

\usepackage{float}
\usepackage{multicol}
%\usepackage[hidelinks]{hyperref}
\usepackage{listings}
\usepackage[dvipsnames]{xcolor}
\usepackage{hyperref} % Gestisce gli URL e i collegamenti ipertestuali
\usepackage{breakurl} % Permette di spezzare gli URL lunghi
\usepackage{forest}
\usepackage{tikz}
\usetikzlibrary{trees}
\usepackage{amsmath}
\usepackage{amssymb}

"""


class PDF_Manager:
    
    
    
    class OPERATION(Enum):
        CLEAR = "clear"
        MERGE = "merge"
        LATEX = "latex"
    
        @classmethod
        def avaialableOption(cls) -> List[str]:
            return list(map(lambda c: c.value, cls))
        
        @classmethod
        def toName(cls, value: str):
            for i in cls:
                if i.value == value:
                    return i
            return None
    
    def __init__(self, outputFolder: str) -> None:
        self._outputFolder:str = outputFolder
        
        
    def _isModelInterfaceDecleared(self, model_Interface: LLMInterfaceBase | None) -> bool:
        if model_Interface is None:
            print("Errore: Per questa operazione è neccessario specificare un modello.")
            print(f"I modelli disponibili sono: {OllamaInterface.MODELS.avaialableOption()}")
            print("Operazione annullata")
            return False
        return True
        
        
    def doOperation(self, operation: OPERATION, inputFils: List[str], model_Interface: LLMInterfaceBase | None = None) -> bool:
        match operation:
            case PDF_Manager.OPERATION.CLEAR:
                pass
            
            case PDF_Manager.OPERATION.MERGE:
                self._merge_PDFs(inputFils, self._outputFolder)
            
            case PDF_Manager.OPERATION.LATEX:
                if not self._isModelInterfaceDecleared(model_Interface): return False
                self._toLatex(inputFils, model_Interface)
            
            case _ :
                raise Exception(f"Operazione '{operation}' non implementata")
                
        return True
        
        
    def split_PDF(self) -> None:
        pass
        
      
    def _merge_PDFs(self, file_list: List[str], output_path: str | None = None) -> None:
        merger = PyPDF2.PdfMerger()
        outname_default = "merged.pdf"
        
        for i, file in enumerate(file_list):
            print(f"[{i + 1}/{len(file_list)}] - processing: {file}")
            merger.append(file)
        
        
        # if output_path == None or output_path == "":
        #     output_path = os.path.join(os.getcwd(), outname_default)
            
        # elif os.path.isdir(output_path):
        #     output_path = os.path.join(output_path, outname_default)
        
        # print("scrittura del file...")
        # merger.write(output_path)
        # merger.close()
        result = self._writeFile(outputFolder= output_path, fileName=outname_default, data=merger, addTime=True)
        
        if result[0]:
            logging.info(f"PDF saved in: {result[1]}")
        else:
            logging.info(f"Merging fallied")
            
            
    def _toLatex(self, inputFils: List[str], modelInterface:LLMInterfaceBase) -> None:
        global DEFAULT_PROMPT_v2
        global LATEX_DOCUMENT_DATA
        
        IMG_FOLDER_NAME = "images"
        
        #ollama = OllamaInterface(model=model, host= "192.168.1.200", timeout_s=40)
        
        for i, PDF_PATH in enumerate(inputFils):
            fileName = os.path.split(PDF_PATH)[1].split('.')[0]
            texFIle = f"{fileName}.tex"
            targetFolder = os.path.join(self._outputFolder, f"{fileName}-LaTex")
            imgFolder = os.path.join(targetFolder, IMG_FOLDER_NAME)
            
            if not os.path.exists(targetFolder):
                os.makedirs(targetFolder)

            if not os.path.exists(imgFolder):
                os.makedirs(imgFolder)
        
            logging.info(f"{'-'*60}")
            logging.info("Processando file [{i + 1}/{len(inputFils)}]: {PDF_PATH}")
            logging.info(f"{'-'*60}")
        
            reader: PyPDF2.PdfReader = PyPDF2.PdfReader(PDF_PATH)
            metadata = reader.metadata
            page_number = len(reader.pages)
        
            logging.info("Metadati del PDF:")
            logging.info(f"- Titolo: {metadata.title}")
            logging.info(f"- Autore: {metadata.author}")
            logging.info(f"- Numero di pagine: {page_number}")
            logging.info(f"{'-'*60}")
            
            #Clear
            with open(os.path.join(targetFolder, texFIle), mode='w') as outputStream:
                outputStream.write("")
        
            with open(os.path.join(targetFolder, texFIle), mode='a') as outputStream:
                #if model.value["image"]:
                doc = fitz.open(PDF_PATH)
                
                outputStream.write(LATEX_DOCUMENT_DATA)
                outputStream.write("\\begin{document}\n")
                
                for j, page in enumerate(doc):
                    logging.info(f"processando pagina [{j+1}/{len(doc)}]")
                    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
                    
                    # Converti l'immagine in BytesIO (senza salvarla su disco)
                    image_bytes = io.BytesIO(pix.tobytes("png"))
                    image = Image.open(image_bytes)
                    
                    # with open(os.path.join(targetFolder, "pagina1.png"), "wb") as f:
                    #     f.write(image_bytes.getvalue())
                    # return
                
                    # Codifica l'immagine in Base64 per Ollama
                    #image_base64 = base64.b64encode(image_bytes.getvalue()).decode("utf-8")
                    #prompt = "Converti questa imamgine in Latex. Utilizza un blocco di codice."
                    failure_count = 0
        
                    try:
                        while True:
                            #response = ollama.chat(content=DEFAULT_PROMPT_v2, image_base64=image_base64)
                            msg: str = ""
                            response = modelInterface.chat(prompt=DEFAULT_PROMPT_v2, image=image)
                            
                            if isinstance(response, GenerateContentResponse):
                                msg = response.text
                                
                            elif isinstance(response, dict):
                                msg = response["message"]["content"]
                        
                            if msg.find("```latex") != -1:
                                break
                            
                            if failure_count:
                                print()
                            
                            print(f"non è stato trovato ```latex``` nel documento. Tentativo numero {failure_count}")
                            failure_count += 1
                            
                            if failure_count >= 5:
                                raise Exception("Non è stato trovato ```latex``` nel documento")
                    
                    except Exception as e:
                        #SALTO LA PAGINA
                        if isinstance(e, httpx.ReadTimeout):
                            p1 = "\n\t\\begin{center}\\Large{\\textbf{"
                            p2 = f"[MISSING PAGE {j + 1}]"
                            p3 = "}}\\end{center}\n"
                            outputStream.write(f"{p1}{p2}{p3}") 
                            logging.error("TimeOut")
                            continue
                        
                        logging.error(e)
                        return
                                    
                    
                    latex = msg.split("```latex")[1].split("```")[0]
                    
                    match = re.search(r"\\begin{document}(.*?)\\end{document}", latex, re.DOTALL)
                    
                    if match:
                        latex = match.group(1).strip()
                    
                    toReplace = {
                        r"\\maketitle" : "",
                        r"\\title{(.*?)}" : "",
                        r"\\title\*{(.*?)}" : "",
                        r"\\author{(.*?)}" : "",
                        r"\\date{(.*?)}" : "",
                        r"\\begin{document}" : "",
                        r"\\end{document}" : "",
                        r"section\*" : "section",
                        r"\\documentclass{(.*?)}" : "",
                        r"\\usepackage{(.*?)}" : "",
                        r"\\usepackage{(.*?)}\[(.*?)\]" : "",
                        r"\\usepackage\[(.*?)\]{(.*?)}" : "",
                        '\n': '\n\t'
                    }
                                            
                    for key_pattern in toReplace.keys():
                        latex = re.sub(pattern = key_pattern, repl=toReplace[key_pattern], string=latex)
                        
                    #latex = latex.replace('\n', '\n\t')
                        
                    # documentBody:str = match.group(1).strip() if match else latex
                    # documentBody = documentBody.replace("\\maketitle", '')
                    outputStream.write(latex) 
                    outputStream.flush() 
                
                outputStream.write("\n\\end{document}\n")
                outputStream.flush() 
                    
                    
        
        # for i in range(page_number):
            
        #     print(f"Analizzando pagina [{i+1}/{page_number}]", end='\r')
        #     result = extract_page_data(i)
        
        
        
    def _writeFile(self, outputFolder:str, fileName: str, data: str | PyPDF2.PdfMerger, addTime: bool = False, extension: str = ".pdf") -> Tuple[str, bool]:
        temp = fileName.split(".")
        fileName = temp[0]
        fileName = f"{fileName}" + (f"_{datetime.today().strftime('[%Y-%m-%d]_[%H-%M-%S]')}" if addTime else "")
        fileIndex = 0
        path: str = os.path.join(outputFolder, fileName)
        
        try:
           
            while os.path.exists(path):
                fileIndex += 1
                path = os.path.join(outputFolder, f"{fileName} ({fileIndex})")
            
            path = path + extension
            logging.info(f"writing on {path}")
            
            if isinstance(data , str):
                with open(path, "w") as file:
                    file.write(data)    
            
            elif isinstance(data, PyPDF2.PdfMerger):
                data.write(path)
                data.close()
                
        except Exception as e:
            print(e)
            logging.error(e)
            return (False, path)
            
        return (True, path)