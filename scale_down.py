from typing import Callable
from PIL import Image
import argparse
import os


def each_image(dir: str, transform_fn: Callable[[Image, str], None]):
    files = os.listdir(dir)
    for name in files:
        filepath = os.path.join(dir, name)
        try:
            img = Image.open(filepath)
            transform_fn(img, filepath)
        except FileExistsError or FileNotFoundError:
            print(f"{filepath} is not a valid image")


def main():
    parser = argparse.ArgumentParser(description="scale down images")
    parser.add_argument("path", type=str, help="directory containing images")
    parser.add_argument(
        "-height", "--height", type=int, help="max height", default=1280
    )
    args = parser.parse_args()

    new_height = args.height

    def scale_down(img: Image, path: str):
        orig_width, orig_height = img.size
        scaling_factor = new_height / orig_height
        new_width = orig_width * scaling_factor
        new_img = img.resize((int(new_width), int(new_height)), Image.LANCZOS)
        print("saving to ", path)
        new_img.save(path)

    each_image(args.path, scale_down)


main()
