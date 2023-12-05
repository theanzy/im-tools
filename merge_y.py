import argparse
import os
from PIL import Image


def merge_frames_v(images: list[Image.Image]) -> Image.Image:
    widths = map(lambda img: img.width, images)
    img_w = max(widths)
    img_h = images[0].height
    spritesheet_width = img_w
    spritesheet_height = img_h * len(images)
    spritesheet = Image.new(
        'RGBA', (int(spritesheet_width), int(spritesheet_height)))
    print(spritesheet.width, spritesheet.height)

    for i, frame in enumerate(images):
        left = 0
        right = frame.width
        top = i * frame.height
        bottom = top + frame.height
        box = (left, top, right, bottom)
        cut_frame = frame.crop((0, 0, frame.width, frame.height))
        print('i', i)
        spritesheet.paste(cut_frame, box)

    return spritesheet


def get_frames(dir: str) -> list[Image.Image]:
    frames = []
    files = os.listdir(dir)
    for name in files:
        filepath = os.path.join(dir, name)
        try:
            img = Image.open(filepath)
            frames.append(img)
        except:
            print(f'{filepath} is not a valid image')
    return frames


def main():
    parser = argparse.ArgumentParser(description='merge images verically')
    parser.add_argument('path', type=str,
                        help='directory containing images')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='output path')
    args = parser.parse_args()

    dirpath = args.path
    outpath = args.output

    frames = get_frames(dirpath)
    sprite = merge_frames_v(frames)
    sprite.save(outpath, "PNG")


if __name__ == '__main__':
    main()
