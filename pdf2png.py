import argparse
import os
from concurrent.futures import ProcessPoolExecutor

import fitz  # pdf
from tqdm import tqdm


def render_specific_page(pdf_path: str, page_index: int, out_dir: str, dpi: int):
    """
    Worker function: Opens the PDF, renders one page, then closes the PDF.
    This ensures minimal RAM footprint per process.
    """
    try:
        with fitz.open(pdf_path) as doc:
            page = doc.load_page(page_index)
            pix = page.get_pixmap(dpi=dpi)
            output_path = os.path.join(out_dir, f'page_{page_index + 1:04d}.png')
            pix.save(output_path)
    except Exception as e:
        return f'Error on page {page_index} : {e}'

    return None


def convert_pdf(pdf_path: str, out_dir: str, dpi=150, max_processes: int = 1):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    total_pages = 0
    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
    if total_pages == 0:
        raise Exception('the pdf file is blank')

    # max_processes: Lower this if you are running out of RAM
    with ProcessPoolExecutor(max_workers=max_processes) as executor:
        tasks = [
            executor.submit(render_specific_page, pdf_path, i, out_dir, dpi)
            for i in range(total_pages)
        ]
        # track progress
        for future in tqdm(tasks, total=total_pages, desc='Rendering PNGs'):
            result = future.result()
            if result:
                print(result)


def main():
    parser = argparse.ArgumentParser(
        description='Convert multi-pages PDF file to multiple png images'
    )
    parser.add_argument('path', type=str, help='pdf file to convert')
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        required=True,
        help='directory containing png images',
    )
    args = parser.parse_args()
    file_path = args.path
    out_dir = args.output
    cpu_count = os.cpu_count()
    if cpu_count is None:
        cpu_count = 1
    else:
        cpu_count = int(cpu_count / 2)
    convert_pdf(file_path, out_dir, dpi=200, max_processes=cpu_count)


if __name__ == '__main__':
    main()
