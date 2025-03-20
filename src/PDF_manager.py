from enum import Enum
from typing import List, Tuple
import time
from datetime import datetime
import os
import logging

import PyPDF2


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
        
        
    def split_PDF(self) -> None:
        pass
        
      
    def merge_PDFs(self, file_list: List[str], output_path: str | None = None) -> None:
        merger = PyPDF2.PdfMerger()
        outname_default = "merged.pdf"
        
        for i, file in enumerate(file_list):
            print(f"[{i + 1}/{len(file_list)}] - processing: {file}")
            merger.append(file)
        
        
        if output_path == None or output_path == "":
            output_path = os.path.join(os.getcwd(), outname_default)
            
        elif os.path.isdir(output_path):
            output_path = os.path.join(output_path, outname_default)
        
        # print("scrittura del file...")
        # merger.write(output_path)
        # merger.close()
        result = self._writeFile(data=merger)
        
        if result[0]:
            logging.info(f"PDF saved in: {result[1]}")
        else:
            logging.info(f"Merging fallied")
        
    def _writeFile(self, folder:str, fileName: str, data: str | PyPDF2.PdfMerger, addTime: bool = False) -> Tuple[str, bool]:
        temp = fileName.split(".")
        extension = temp[1]
        fileName = temp[0]
        fileName = f"{fileName} - {datetime.date()} - {datetime.hour}:{datetime.minute}:{datetime.second}"
        fileIndex = 0
        path: str = os.path.join(folder, fileName)
        
        try:
            
            while os.path.exists(path):
                fileIndex += 1
                path = os.path.join(folder, f"{fileName} ({fileIndex})")
              
            fileName = fileName.join(f".{extension}")    
            logging.info(f"writing on {path}")
            
            if isinstance(data , str):
                with open(path, "w") as file:
                    file.write(data)    
            
            elif isinstance(data, PyPDF2.PdfMerger):
                data.write(path)
                data.close()
                
        except Exception as e:
            logging.error(e)
            return (False, path)
            
        return (True, path)