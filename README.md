# gptpdf-LaTeX

This is a fork of the [gptpdf](https://github.com/CosmosShadow/gptpdf) repository. Instead of using markdown, the LLM will output LaTeX code.
Using VLLM (like GPT-4o) to parse PDF into markdown.

Our approach is very simple (only 293 lines of code), but can almost perfectly parse typography, math formulas, tables, pictures, charts, etc.

Average cost per page: $0.013

This package use [GeneralAgent](https://github.com/CosmosShadow/GeneralAgent) lib to interact with OpenAI API.

[pdfgpt-ui](https://github.com/daodao97/gptpdf-ui) is a visual tool based on gptpdf.



## Process steps

1. Use the PyMuPDF library to parse the PDF to find all non-text areas and mark them, for example:

![](docs/demo.jpg)

2. Use a large visual model (such as GPT-4o) to parse and get a markdown file.


## Usage

### Local Usage

```python
from gptpdf import parse_pdf
api_key = 'Your OpenAI API Key'
content, image_paths = parse_pdf(pdf_path, api_key=api_key)
print(content)
```

See more in [examples/PDF_to_LaTeX.py](examples/PDF_to_LaTeX.py)


## API

### parse_pdf

**Function**: 
```
def parse_pdf(
        pdf_path: str,
        output_dir: str = './',
        prompt: Optional[Dict] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = 'gpt-4o',
        verbose: bool = False,
        gpt_worker: int = 1,
        document_initial_text: str = '',
        document_final_text: str = ''
) -> Tuple[str, List[str]]:
```

Parses a PDF file into a Markdown file and returns the Markdown content along with all image paths.

**Parameters**:

- **pdf_path**: *str*  
  Path to the PDF file

- **output_dir**: *str*, default: './'  
  Output directory to store all images and the Markdown file

- **api_key**: *Optional[str]*, optional  
  OpenAI API key. If not provided, the `OPENAI_API_KEY` environment variable will be used.

- **base_url**: *Optional[str]*, optional  
  OpenAI base URL. If not provided, the `OPENAI_BASE_URL` environment variable will be used. This can be modified to call other large model services with OpenAI API interfaces, such as `GLM-4V`.

- **model**: *str*, default: 'gpt-4o'  
  OpenAI API formatted multimodal large model. If you need to use other models, such as:
  - [qwen-vl-max](https://help.aliyun.com/zh/dashscope/developer-reference/compatibility-of-openai-with-dashscope) 
  - [GLM-4V](https://open.bigmodel.cn/dev/api#glm-4v)
  - [Yi-Vision](https://platform.lingyiwanwu.com/docs) 
  - Azure OpenAI, by setting the `base_url` to `https://xxxx.openai.azure.com/` to use Azure OpenAI, where `api_key` is the Azure API key, and the model is similar to `azure_xxxx`, where `xxxx` is the deployed model name (tested).

- **verbose**: *bool*, default: False  
  Verbose mode. When enabled, the content parsed by the large model will be displayed in the command line.

- **gpt_worker**: *int*, default: 1  
  Number of GPT parsing worker threads. If your machine has better performance, you can increase this value to speed up the parsing.

- **prompt**: *dict*, optional  
  If the model you are using does not match the default prompt provided in this repository and cannot achieve the best results, we support adding custom prompts. The prompts in the repository are divided into three parts:
  - `prompt`: Mainly used to guide the model on how to process and convert text content in images.
  - `rect_prompt`: Used to handle cases where specific areas (such as tables or images) are marked in the image.
  - `role_prompt`: Defines the role of the model to ensure the model understands it is performing a PDF document parsing task.

- **document_initial_text**: *str*, default: ''
    Initial text to be added to the document before the outputted content.
- **document_final_text**: *str*, default: ''
    Final text to be added to the document after the outputted content.

  You can pass custom prompts in the form of a dictionary to replace any of the prompts. Here is an example:

```
prompt = {
    "prompt": "Custom prompt text",
    "rect_prompt": "Custom rect prompt",
    "role_prompt": "Custom role prompt"
}

content, image_paths = parse_pdf(
    pdf_path=pdf_path,
    output_dir='./output',
    model="gpt-4o",
    prompt=prompt,
    verbose=False,
)
```



**args**: LLM other parameters, such as `temperature`, `top_p`, `max_tokens`, `presence_penalty`, `frequency_penalty`, etc.
