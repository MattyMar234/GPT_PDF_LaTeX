import os
import re
from typing import List, Tuple, Optional, Dict, Set
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import fitz  # PyMuPDF
import shapely.geometry as sg
from shapely.geometry.base import BaseGeometry
from shapely.validation import explain_validity
import concurrent.futures

DEFAULT_PROMPT = """Using LaTeX syntax, convert the text recognised in the image into LaTeX format for output. You must do:
1. output the same language as the one that uses the recognised image, for example, for fields recognised in English, the output must be in English.
2. don't interpret the text which is not related to the output, and output the content in the image directly. For example, it is strictly forbidden to output examples like ``Here is the LaTeX text I generated based on the content of the image:'' Instead, you should output LaTeX code directly.
3. Content should not be included in ```latex ```, paragraph formulas should be in the form of $$ $$, in-line formulas should be in the form of $ $$, long straight lines should be ignored, and page numbers should be ignored.
Again, do not interpret text that is not relevant to the output, and output the content in the image directly.
In each page you could possibly find a title, so use section or subsection etc.
"""
DEFAULT_RECT_PROMPT = """Areas are marked in the image with a red box and a name (%s) DO NOT CHANGE THE %s. If the regions are tables or images, use 
\\begin{center}
    	\\includegraphics[width=0.5\\linewidth,trim={0 0 0 0},clip]{%s} %trim={<left> <lower> <right> <upper>}
\\end{center}
form to insert into the output, otherwise output the text content directly. You could also use tikz if possible, but prefer images if the tikz is complex.
If instead the image is taking, for example the title, text and the correct part that should be the image, you could use the trim option in the includegraphics to remove the unwanted part (as it could be already present in the text version).
"""
DEFAULT_ROLE_PROMPT = """You are a PDF document parser that outputs the content of images using latex syntax. Remember to always use the latex syntax.
"""


def _is_near(rect1: BaseGeometry, rect2: BaseGeometry, distance: float = 20) -> bool:
    """
    Check if two rectangles are near each other if the distance between them is less than the target.
    """
    return rect1.buffer(0.1).distance(rect2.buffer(0.1)) < distance


def _is_horizontal_near(rect1: BaseGeometry, rect2: BaseGeometry, distance: float = 100) -> bool:
    """
    Check if two rectangles are near horizontally if one of them is a horizontal line.
    """
    result = False
    if abs(rect1.bounds[3] - rect1.bounds[1]) < 0.1 or abs(rect2.bounds[3] - rect2.bounds[1]) < 0.1:
        if abs(rect1.bounds[0] - rect2.bounds[0]) < 0.1 and abs(rect1.bounds[2] - rect2.bounds[2]) < 0.1:
            result = abs(rect1.bounds[3] - rect2.bounds[3]) < distance
    return result


def _union_rects(rect1: BaseGeometry, rect2: BaseGeometry) -> BaseGeometry:
    """
    Union two rectangles.
    """
    return sg.box(*(rect1.union(rect2).bounds))


def _merge_rects(rect_list: List[BaseGeometry], distance: float = 20, horizontal_distance: Optional[float] = None) -> \
        List[BaseGeometry]:
    """
    Merge rectangles in the list if the distance between them is less than the target.
    """
    merged = True
    while merged:
        merged = False
        new_rect_list = []
        while rect_list:
            rect = rect_list.pop(0)
            for other_rect in rect_list:
                if _is_near(rect, other_rect, distance) or (
                        horizontal_distance and _is_horizontal_near(rect, other_rect, horizontal_distance)):
                    rect = _union_rects(rect, other_rect)
                    rect_list.remove(other_rect)
                    merged = True
            new_rect_list.append(rect)
        rect_list = new_rect_list
    return rect_list


def _adsorb_rects_to_rects(source_rects: List[BaseGeometry], target_rects: List[BaseGeometry], distance: float = 10) -> \
        Tuple[List[BaseGeometry], List[BaseGeometry]]:
    """
    Adsorb a set of rectangles to another set of rectangles.
    """
    new_source_rects = []
    for text_area_rect in source_rects:
        adsorbed = False
        for index, rect in enumerate(target_rects):
            if _is_near(text_area_rect, rect, distance):
                rect = _union_rects(text_area_rect, rect)
                target_rects[index] = rect
                adsorbed = True
                break
        if not adsorbed:
            new_source_rects.append(text_area_rect)
    return new_source_rects, target_rects


def _parse_rects(page: fitz.Page) -> List[Tuple[float, float, float, float]]:
    """
    Parse drawings in the page and merge adjacent rectangles.
    """
    drawings = page.get_drawings()
    is_short_line = lambda x: abs(x['rect'][3] - x['rect'][1]) < 1 and abs(x['rect'][2] - x['rect'][0]) < 30
    drawings = [drawing for drawing in drawings if not is_short_line(drawing)]
    rect_list = [sg.box(*drawing['rect']) for drawing in drawings]
    images = page.get_image_info()
    image_rects = [sg.box(*image['bbox']) for image in images]
    rect_list += image_rects
    merged_rects = _merge_rects(rect_list, distance=10, horizontal_distance=100)
    merged_rects = [rect for rect in merged_rects if explain_validity(rect) == 'Valid Geometry']
    is_large_content = lambda x: (len(x[4]) / max(1, len(x[4].split('\n')))) > 5
    small_text_area_rects = [sg.box(*x[:4]) for x in page.get_text('blocks') if not is_large_content(x)]
    large_text_area_rects = [sg.box(*x[:4]) for x in page.get_text('blocks') if is_large_content(x)]
    _, merged_rects = _adsorb_rects_to_rects(large_text_area_rects, merged_rects, distance=0.1)
    _, merged_rects = _adsorb_rects_to_rects(small_text_area_rects, merged_rects, distance=5)
    merged_rects = _merge_rects(merged_rects, distance=10)
    merged_rects = [rect for rect in merged_rects if
                    rect.bounds[2] - rect.bounds[0] > 20 and rect.bounds[3] - rect.bounds[1] > 20]
    return [rect.bounds for rect in merged_rects]


def _parse_pdf_to_images(
        pdf_path: str,
        output_dir: str = './',
        output_dir_images: Optional[str] = None,
        use_sequential_naming: bool = False
) -> List[Tuple[str, List[str]]]:
    """
    Parse PDF to images and save to output_dir.
    """
    pdf_document = fitz.open(pdf_path)
    image_infos = []

    image_dir = output_dir_images if output_dir_images else output_dir

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    def get_next_image_number():
        existing_images = [f for f in os.listdir(image_dir) if f.startswith('image') and f.endswith('.png')]
        if not existing_images:
            return 1
        numbers = [int(re.search(r'image(\d+)\.png', f).group(1)) for f in existing_images]
        return max(numbers) + 1

    for page_index, page in enumerate(pdf_document):
        logging.info(f'parse page: {page_index}')
        rect_images = []
        rects = _parse_rects(page)

        for index, rect in enumerate(rects):
            fitz_rect = fitz.Rect(rect)
            # Save page as image
            pix = page.get_pixmap(clip=fitz_rect, matrix=fitz.Matrix(4, 4))

            if use_sequential_naming:
                name = f'image{get_next_image_number()}.png'
            else:
                name = f'{page_index}_{index}.png'

            image_path = os.path.join(image_dir, name)
            pix.save(image_path)
            rect_images.append(name)
            # # Draw a red rectangle on the page
            big_fitz_rect = fitz.Rect(fitz_rect.x0 - 1, fitz_rect.y0 - 1, fitz_rect.x1 + 1, fitz_rect.y1 + 1)
            # hollow rectangle
            page.draw_rect(big_fitz_rect, color=(1, 0, 0), width=1)
            # Draw rectangular area (solid)
            # page.draw_rect(big_fitz_rect, color=(1, 0, 0), fill=(1, 0, 0))
            # Write the index name of the rectangle in the upper left corner inside the rectangle, add some offsets
            text_x = fitz_rect.x0 + 2
            text_y = fitz_rect.y0 + 10
            text_rect = fitz.Rect(text_x, text_y - 9, text_x + 80, text_y + 2)
            # Draw white background rectangle
            page.draw_rect(text_rect, color=(1, 1, 1), fill=(1, 1, 1))
            # Insert text with a white background
            page.insert_text((text_x, text_y), name, fontsize=10, color=(1, 0, 0))

        page_image_with_rects = page.get_pixmap(matrix=fitz.Matrix(3, 3))
        page_image = os.path.join(output_dir, f'{page_index}.png')
        page_image_with_rects.save(page_image)
        image_infos.append((page_image, rect_images))

    pdf_document.close()
    return image_infos


def _gpt_parse_images(
        image_infos: List[Tuple[str, List[str]]],
        document_initial_text: str,
        document_final_text: str,
        prompt_dict: Optional[Dict] = None,
        output_dir: str = './',
        output_dir_images: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = 'gpt-4o',
        verbose: bool = False,
        gpt_worker: int = 1,
        cleanup_unused: bool = False,
        **args
) -> Tuple[str, Set[str]]:
    """
    Parse images to latex content and track used images.
    """
    from GeneralAgent import Agent

    if isinstance(prompt_dict, dict) and 'prompt' in prompt_dict:
        prompt = prompt_dict['prompt']
        logging.info("prompt is provided, using user prompt.")
    else:
        prompt = DEFAULT_PROMPT
        logging.info("prompt is not provided, using default prompt.")
    if isinstance(prompt_dict, dict) and 'rect_prompt' in prompt_dict:
        rect_prompt = prompt_dict['rect_prompt']
        logging.info("rect_prompt is provided, using user prompt.")
    else:
        rect_prompt = DEFAULT_RECT_PROMPT
        logging.info("rect_prompt is not provided, using default prompt.")
    if isinstance(prompt_dict, dict) and 'role_prompt' in prompt_dict:
        role_prompt = prompt_dict['role_prompt']
        logging.info("role_prompt is provided, using user prompt.")
    else:
        role_prompt = DEFAULT_ROLE_PROMPT
        logging.info("role_prompt is not provided, using default prompt.")

    used_images = set()

    def _process_page(index: int, image_info: Tuple[str, List[str]]) -> Tuple[int, str]:
        logging.info(f'gpt parse page: {index}')
        agent = Agent(role=role_prompt, api_key=api_key, base_url=base_url, disable_python_run=True, model=model,
                      **args)
        page_image, rect_images = image_info
        local_prompt = prompt
        if rect_images:
            local_prompt += rect_prompt + ', '.join(rect_images)
        content = agent.run([local_prompt, {'image': page_image}], display=verbose)
        return index, content

    contents = [None] * len(image_infos)
    with concurrent.futures.ThreadPoolExecutor(max_workers=gpt_worker) as executor:
        futures = [executor.submit(_process_page, index, image_info) for index, image_info in enumerate(image_infos)]
        for future in concurrent.futures.as_completed(futures):
            index, content = future.result()

            if '```latex' in content:
                content = content.replace('```latex\n', '')
                last_backticks_pos = content.rfind('```')
                if last_backticks_pos != -1:
                    content = content[:last_backticks_pos] + content[last_backticks_pos + 3:]
            if '```' in content:
                content = content.replace('```\n', '')
                last_backticks_pos = content.rfind('```')
                if last_backticks_pos != -1:
                    content = content[:last_backticks_pos] + content[last_backticks_pos + 3:]

            for image_name in image_infos[index][1]:
                if image_name in content:
                    used_images.add(image_name)

            contents[index] = content

    final_content = document_initial_text + '\n\n' + '\n\n'.join(contents) + '\n\n' + document_final_text

    output_path = os.path.join(output_dir, 'output.tex')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)

    return final_content, used_images


def parse_pdf(
        pdf_path: str,
        output_dir: str = './',
        output_dir_images: Optional[str] = None,
        use_sequential_naming: bool = False,
        cleanup_unused: bool = False,
        prompt: Optional[Dict] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = 'gpt-4o',
        verbose: bool = False,
        gpt_worker: int = 1,
        document_initial_text: str = '',
        document_final_text: str = '',
        **args
) -> Tuple[str, List[str]]:
    """
    Parse a PDF file to a latex file.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory for general output
        output_dir_images: Optional directory specifically for images
        use_sequential_naming: If True, uses sequential naming based on existing files
        cleanup_unused: If True, removes images that aren't referenced in the final document
        prompt: Optional dictionary containing custom prompts
        api_key: Optional API key for GPT
        base_url: Optional base URL for API
        model: Model to use for GPT
        verbose: If True, shows detailed output
        gpt_worker: Number of concurrent GPT workers
        document_initial_text: Text to prepend to the output
        document_final_text: Text to append to the output
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_infos = _parse_pdf_to_images(
        pdf_path,
        output_dir=output_dir,
        output_dir_images=output_dir_images,
        use_sequential_naming=use_sequential_naming
    )

    content, used_images = _gpt_parse_images(
        image_infos=image_infos,
        output_dir=output_dir,
        output_dir_images=output_dir_images,
        prompt_dict=prompt,
        api_key=api_key,
        base_url=base_url,
        model=model,
        verbose=verbose,
        gpt_worker=gpt_worker,
        document_initial_text=document_initial_text,
        document_final_text=document_final_text,
        cleanup_unused=cleanup_unused,
        **args
    )

    all_rect_images = []
    img_dir = output_dir_images if output_dir_images else output_dir

    # Collect all generated images and handle cleanup
    for page_image, rect_images in image_infos:
        if not verbose and os.path.exists(page_image):
            os.remove(page_image)
        all_rect_images.extend(rect_images)

        # Remove unused images if cleanup is enabled
        if cleanup_unused:
            for img in rect_images:
                if img not in used_images:
                    img_path = os.path.join(img_dir, img)
                    if os.path.exists(img_path):
                        try:
                            os.remove(img_path)
                            logging.info(f"Removed unused image: {img}")
                        except Exception as e:
                            logging.warning(f"Failed to remove unused image {img}: {e}")

    return content, list(used_images)