import argparse
import os
from PIL import Image
from merge_x import merge_frames_x


def main():
    parser = argparse.ArgumentParser(
        description="walk folder and merge images into strip"
    )
    parser.add_argument("path", type=str, help="path to image file")
    args = parser.parse_args()
    path = args.path

    strip_group = {}
    for dir in os.walk(path):
        filenames: list[str] = dir[2]
        if os.path.splitext(filenames[0])[1] != ".png":
            continue
        for f in filenames:
            ftokens = f.split("_")
            input_path = os.path.normpath(os.path.join(dir[0], f))
            if len(ftokens) > 1:
                if ftokens[0] not in strip_group:
                    strip_group[ftokens[0]] = []
                strip_group[ftokens[0]].append(input_path)
            else:
                strip_group[f.split(".")[0]] = [input_path]

    for name, strips in strip_group.items():
        strip_count = len(strips)
        if strip_count > 1:
            strip_count -= 1
        outname = f"{name}_strip{strip_count:02}.png"
        outdir = ".temp/spritesheets/crops"
        if not os.path.isdir(outdir):
            os.makedirs(outdir, exist_ok=True)
        outpath = os.path.normpath(os.path.join(outdir, outname))
        merge_frames_x([Image.open(f) for f in strips[:strip_count]]).save(outpath)


if __name__ == "__main__":
    main()
