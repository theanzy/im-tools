import argparse
import os
from concurrent.futures import ProcessPoolExecutor
from os.path import join
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm


def crop_document_with_shadows(image_path: str, output_path: str):
    # 1. Load the image
    img = cv2.imread(image_path)
    if img is None:
        return f'Fail to read image path="{image_path}"'

    # 2. Convert to grayscale to simplify color data
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Apply a threshold to separate the document from the white background
    # Since the background is white (255), we use THRESH_BINARY_INV to make
    # the document white and the background black for contour detection.
    # We use Otsu's method to automatically calculate the best threshold value.
    _, thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)

    # 4. Find contours (shapes) in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # 5. Pick the largest contour by area (the document)
        largest_contour = max(contours, key=cv2.contourArea)

        # 6. Get the bounding box
        x, y, w, h = cv2.boundingRect(largest_contour)

        # 7. Crop and save
        # We add a tiny buffer (optional) to ensure we don't clip the paper
        cropped_img = img[y : y + h, x : x + w]
        cv2.imwrite(output_path, cropped_img)
    else:
        cv2.imwrite(output_path, img)


def crop_parallel(
    in_dir: str,
    out_dir: str,
    max_processes: int,
):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    directory = Path(in_dir)
    filepaths = [f for f in directory.iterdir() if f.suffix.lower() in image_extensions]

    with ProcessPoolExecutor(max_workers=max_processes) as executor:
        tasks = [
            executor.submit(
                crop_document_with_shadows,
                join(in_dir, str(f.absolute())),
                join(out_dir, f'{f.stem}_cropped{f.suffix}'),
            )
            for f in filepaths
        ]

        for future in tqdm(tasks, total=len(filepaths), desc='Cropping'):
            result = future.result()
            if result:
                print(result)


def main():
    parser = argparse.ArgumentParser(description='Crop document')
    parser.add_argument('path', type=str, help='directory containing frames')
    parser.add_argument(
        '-o', '--output', type=str, required=True, help='directory containing frames'
    )

    args = parser.parse_args()
    in_dir = args.path
    out_dir = args.output
    cpu_count = os.cpu_count()
    if cpu_count is None:
        cpu_count = 1
    else:
        cpu_count = cpu_count // 2
    crop_parallel(in_dir, out_dir, cpu_count)


if __name__ == '__main__':
    main()
