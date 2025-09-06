from typing import Any, Callable
import argparse
import os
import numpy as np
from skimage import io
from skimage.color import rgb2gray
from skimage.transform import rotate
from deskew import determine_skew


def each_image(dir: str, transform_fn: Callable[[Any, str], None]):
    files = os.listdir(dir)
    for name in files:
        filepath = os.path.join(dir, name)
        try:
            img = io.imread(filepath)
            transform_fn(img, filepath)
        except FileExistsError or FileNotFoundError:
            print(f"{filepath} is not a valid image")


def deskew_img(img: Any, path: str):
    grayscale = rgb2gray(img)
    angle = determine_skew(grayscale)
    rotated = rotate(img, angle, resize=True) * 255
    io.imsave(path, rotated.astype(np.uint8))


def main():
    parser = argparse.ArgumentParser(description="scale down images")
    parser.add_argument("path", type=str, help="directory containing images")
    args = parser.parse_args()
    each_image(args.path, deskew_img)


main()
