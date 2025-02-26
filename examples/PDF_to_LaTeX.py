# Working principle:
# 1. Ask the user for the path to the PDF file (Also by drag and drop into the terminal)
# 2. Ask the user for the path to the output directory (By pre-defined paths)
# 3. Parse the PDF file and extract the text and images
# 4. Save the text to a .tex file and images to the output directory

# Before executing the script, make sure to install the required packages:
# pip install PyMuPDF shapely GeneralAgent
# Also change the path to the gptpdf_LaTeX package in sys.path.append() to your own path,
# the APIKEY in the run_script() function and the paths in the list_of_outputs.

#from .parse import parse_pdf
import os
import sys
import dotenv
sys.path.append('PATH_TO\\gptpdf_LaTeX') # Add the path to the gptpdf_LaTeX package (change this to your own path)
dotenv.load_dotenv()
from gptpdf.parse import parse_pdf

import dotenv
dotenv.load_dotenv()

document_initial_text= """
\\documentclass[a4paper,14pt]{extarticle}
\\usepackage{graphicx, mathptmx, amsmath, amsfonts, url, hyperref, tikz, float}
\\usepackage{amsfonts}
\\usepackage{amsmath}
\\usepackage{textcomp}
\\usepackage{xcolor}
\\usepackage{geometry}

\\title{TITLE} %IS or SEF or SPM
\\author{AUTHOR}
\\date{DATE}

\\begin{document}

    \\maketitle
"""

document_final_text= """
\\end{document}
"""

pdf_path = ""
output_dir = ""
output_dir_images = ""

def run_script():
    from gptpdf import parse_pdf
    api_key = "APIKEY"
    base_url = "https://api.openai.com/v1"

    # ---- PATH MANAGEMENT ----
    pdf_path = input("Enter the path to the PDF file: ")
    pdf_path = pdf_path.replace('\"', '')
    list_of_outputs = {"KEYTOSHOW": "OUTPUTPATH1", "KEY2": "PATH2"}
    keys = list(list_of_outputs.keys()) # Get the list of keys
    print("Please choose one of the following options:") # Display a numbered list of keys
    for i, key in enumerate(keys, start=1):
        print(f"{i}. {key}")
    try: # Prompt the user for their selection
        choice = int(input("Enter the number of your choice: "))
        if 1 <= choice <= len(keys):
            selected_key = keys[choice - 1]
            selected_path = list_of_outputs[selected_key]
            print(f"You selected '{selected_key}' with path: {selected_path}")
            output_dir = selected_path
            output_dir_images = output_dir + '\\images\\'
        else:
            print("Invalid choice. Please run the program again and choose a valid number.")
    except ValueError:
        print("Please enter a valid number.")
        exit()
    # -------------------

    content, image_paths = parse_pdf(pdf_path, output_dir=output_dir, api_key=api_key, model='gpt-4o', gpt_worker=6, document_initial_text=document_initial_text, document_final_text=document_final_text, base_url=base_url, output_dir_images=output_dir_images, cleanup_unused=True, use_sequential_naming=True)
    print(content)
    print(image_paths)
    # also output_dir/output.tex is generated

run_script()
exit()
