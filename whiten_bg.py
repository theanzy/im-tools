import argparse
import os
from concurrent.futures import ProcessPoolExecutor
from os.path import basename, join
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm


def estimate_background(img: np.ndarray, blur_sigma: int = 21) -> np.ndarray:
    """
    Estimates the slowly-varying background illumination (shadows, yellowing)
    by dilating then heavily blurring each channel.  The result represents
    what the image would look like with no foreground content at all.
    """
    planes = []
    for ch in cv2.split(img):
        dilated = cv2.dilate(ch, np.ones((7, 7), np.uint8))
        bg      = cv2.GaussianBlur(dilated, (0, 0), blur_sigma, blur_sigma)
        planes.append(bg)
    return cv2.merge(planes)


def build_stroke_mask(img: np.ndarray, sensitivity: int = 40) -> np.ndarray:
    """
    Returns a binary mask (255 = stroke pixel, 0 = background pixel).

    Strategy:
      - Convert to grayscale, apply adaptive threshold to find dark strokes.
      - Also detect edges (Canny) to catch faint / low-contrast marks.
      - Merge both and dilate slightly so stroke edges are fully protected.

    sensitivity controls how aggressively faint strokes are included (0-100).
    Higher → more pixels classified as strokes (safer for very light marks).
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ── Adaptive threshold: dark pixels relative to their local neighbourhood
    block = max(11, (sensitivity // 5) * 2 + 11)   # must be odd
    c_val = max(2, 15 - sensitivity // 10)
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block, c_val
    )

    # ── Canny edge map: catches faint strokes that adaptive thresh might miss
    lo = max(5,  40 - sensitivity // 2)
    hi = max(30, 120 - sensitivity)
    edges = cv2.Canny(gray, lo, hi)

    # ── Union
    stroke_mask = cv2.bitwise_or(thresh, edges)

    # ── Dilate to create a safe "halo" around each stroke
    halo = max(3, sensitivity // 15)
    k    = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (halo * 2 + 1,) * 2)
    stroke_mask = cv2.dilate(stroke_mask, k)

    return stroke_mask


def remove_shadows_bg_only(img: np.ndarray,
                            stroke_mask: np.ndarray,
                            blur_sigma: int = 21) -> np.ndarray:
    """
    Applies illumination normalisation ONLY to background pixels.
    Stroke pixels are blended back from the original so they are untouched.
    """
    bg_illumination = estimate_background(img, blur_sigma)

    # Normalise: divide by background, scale to 0-255
    img_f  = img.astype(np.float32)
    bg_f   = bg_illumination.astype(np.float32)
    norm   = np.clip(img_f / (bg_f + 1e-6) * 255, 0, 255).astype(np.uint8)

    # Blend: background pixels come from normalised image,
    #        stroke pixels come from the original (fully protected)
    alpha        = stroke_mask.astype(np.float32) / 255.0          # 1 = stroke
    alpha_3ch    = np.stack([alpha] * 3, axis=-1)
    blended      = (alpha_3ch       * img.astype(np.float32) +
                    (1 - alpha_3ch) * norm.astype(np.float32))
    return np.clip(blended, 0, 255).astype(np.uint8)



def whiten_yellow_background(
    image_path, output_path, sensitivity=40, remove_shadow: bool = False
):
    """
    Converts a yellowish/off-white background to pure white.
    while preserving handwritten or drawn strokes.


    Args:
        image_path:  Path to the input image.
        output_path: Path to save the result. Defaults to <name>_whitened.<ext>.
        sensitivity: How aggressively to target yellow/off-white tones (0–100).
                     Higher = more pixels replaced. Default 40 works well for
                     most scanned documents / aged paper.
        remove_shadow:  Whether to normalise shadows before whitening (default True).
    """
    img = cv2.imread(image_path)
    if img is None:
        return f'Could not read image: {image_path}'


    # ── Step 1: Build stroke mask BEFORE any processing ──────────────────────
    # We must detect strokes on the raw image so shadow-darkened faint strokes
    # are still visible to the detector.
    stroke_mask = build_stroke_mask(img, sensitivity)

    # ── Step 2: Stroke-aware shadow removal ───────────────────────────────────
    if remove_shadow:
        img = remove_shadows_bg_only(img, stroke_mask)

    # ── Step 3: Whiten yellow / cream background ──────────────────────────────
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_y = np.array([10,  5,  180 - sensitivity])
    upper_y = np.array([40, 80 + sensitivity, 255])
    mask_yellow = cv2.inRange(hsv, lower_y, upper_y)

    lower_c = np.array([0,   0,  210 - sensitivity // 2])
    upper_c = np.array([179, 30 + sensitivity // 2, 255])
    mask_cream = cv2.inRange(hsv, lower_c, upper_c)

    bg_mask = cv2.bitwise_or(mask_yellow, mask_cream)

    # Remove stroke pixels from the background mask so we never whiten a stroke
    bg_mask = cv2.bitwise_and(bg_mask, cv2.bitwise_not(stroke_mask))

    # Morphological close to fill gaps
    k       = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    bg_mask = cv2.morphologyEx(bg_mask, cv2.MORPH_CLOSE, k)

    result = img.copy()
    result[bg_mask == 255] = [255, 255, 255]

    # ── Step 4: CLAHE – boost foreground contrast slightly ────────────────────
    lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    l     = clahe.apply(l)
    result = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

    # ── Save ──────────────────────────────────────────────────────────────────
    cv2.imwrite(output_path, result)
    return None



def whiten_bg_parallel(
    in_dir: str,
    out_dir: str,
    max_processes: int,
    sensitivity: int,
    remove_shadow: bool = True,
):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    directory = Path(in_dir)
    file_names = [
        str(f.absolute())
        for f in directory.iterdir()
        if f.suffix.lower() in image_extensions
    ]

    with ProcessPoolExecutor(max_workers=max_processes) as executor:
        tasks = [
            executor.submit(
                whiten_yellow_background,
                join(in_dir, filename),
                join(out_dir, basename(filename)),
                sensitivity,
                remove_shadow,
            )
            for filename in file_names
        ]

        for future in tqdm(tasks, total=len(file_names), desc='Whitening background'):
            result = future.result()
            if result:
                print(result)


def main():
    parser = argparse.ArgumentParser(description='Whiten images')
    parser.add_argument('path', type=str, help='directory containing frames')
    parser.add_argument(
        '-o', '--output', type=str, required=True, help='directory containing frames'
    )
    parser.add_argument(
        '-s',
        '--sensitivity',
        type=int,
        default=40,
        help='0-100: higher = more aggressive on yellow, more protective of '
        'faint strokes (default: 40)',
    )
    parser.add_argument(
        '--remove-shadow', action='store_true', help='Skip shadow removal step'
    )

    args = parser.parse_args()
    out_dir = args.output
    cpu_count = os.cpu_count()
    sensitivity = args.sensitivity

    if cpu_count is None:
        cpu_count = 1
    else:
        cpu_count = int(cpu_count / 2)

    whiten_bg_parallel(args.path, out_dir, cpu_count, sensitivity, args.remove_shadow)


if __name__ == '__main__':
    main()
