import argparse
import os
import re
from flip_x import flip_x
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description="walk folder and flip all images")
    parser.add_argument("path", type=str, help="path to image file")
    args = parser.parse_args()
    path = args.path

    for dir in os.walk(path):
        d: str = dir[0]
        filenames = dir[2]
        if os.path.splitext(filenames[0])[1] != ".png":
            continue
        dirs = d.split(os.path.sep)
        outdir = os.path.normpath(os.path.join(".temp/spritesheets/", *dirs[-3:]))
        for f in filenames:
            sc = re.search(r"[a-z](\d+)\.png", f)
            strip_count = int(sc.group(1))
            imgpath = os.path.join(d, f)
            if not os.path.isdir(outdir):
                os.makedirs(outdir, exist_ok=True)
            outpath = os.path.normpath(os.path.join(os.path.join(outdir, f)))
            flip_x(Image.open(imgpath), strip_count).save(outpath)


if __name__ == "__main__":
    main()
