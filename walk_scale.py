import argparse
import os
from PIL import Image

from scale import scale


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

    outdirs: list[str] = []
    images: list[tuple[str, str]] = []
    for dir in os.walk(path):
        d = dir[0]
        filenames = dir[2]

        if d == path or not filenames or not any(x.endswith(".png") for x in filenames):
            continue

        dirname = os.path.relpath(d, path)
        outdir = os.path.join(output, dirname)

        outdirs.append(outdir)
        for f in filenames:
            if f.endswith(".png"):
                images.append((os.path.join(d, f), os.path.join(outdir, f)))

    for d in outdirs:
        if not os.path.exists(d):
            os.makedirs(d, 0o777)

    for i in images:
        img = Image.open(i[0])
        scale(img, multiplier).save(i[1])


if __name__ == "__main__":
    run()
