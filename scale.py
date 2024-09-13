import argparse
from PIL import Image


def scale(img: Image.Image, multiplier: int):
    w = img.size[0]
    h = img.size[1]
    return img.resize((w * multiplier, h * multiplier), Image.Resampling.LANCZOS)


def run():
    parser = argparse.ArgumentParser(description="scale image by multiplier factor")
    parser.add_argument("path", type=str, help="path to image file")
    parser.add_argument(
        "-o", "--output", type=str, required=True, help="output path of image"
    )
    parser.add_argument(
        "-m", "--multiplier", type=int, required=True, help="scale multiplier"
    )

    args = parser.parse_args()

    path = args.path
    output = args.output
    multiplier = args.multiplier
    try:
        img = Image.open(path)
        result = scale(img, multiplier)
        result.save(output)
    except FileNotFoundError as e:
        print(e)
        raise SystemExit
    except Exception as e:
        print(e)
        raise SystemExit


if __name__ == "__main__":
    run()
