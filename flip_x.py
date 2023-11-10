
import os
from PIL import Image, ImageOps
import argparse


def merge_frames_x(frames: list[Image.Image]) -> Image.Image:
    tile_width = frames[0].width
    tile_height = frames[0].height
    spritesheet_width = tile_width * len(frames)
    spritesheet_height = tile_height
    spritesheet = Image.new(
        'RGBA', (int(spritesheet_width), int(spritesheet_height)))
    for i, frame in enumerate(frames):
        left = i * tile_width
        right = left + tile_width
        top = 0
        bottom = top + tile_height
        box = (left, top, right, bottom)
        cut_frame = frame.crop((0, 0, tile_width, tile_height))

        spritesheet.paste(cut_frame, box)

    return spritesheet


def main():
    parser = argparse.ArgumentParser(description='Images to spritesheet.')
    parser.add_argument('path', type=str,
                        help='path to image')
    parser.add_argument('-n', '--nframe', type=int, required=True,
                        help='number of frames')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='output path')
    args = parser.parse_args()

    img = Image.open(args.path)
    n_frames = args.nframe
    output_path = args.output
    iwidth = img.width / n_frames
    iheight = img.height

    frames: list[Image.Image] = []
    for i in range(0, n_frames):
        i_frame = img.crop((i * iwidth, 0, i * iwidth + iwidth, iheight))
        mirrored = ImageOps.mirror(i_frame)
        frames.append(mirrored)

    sprite = merge_frames_x(frames)
    print(output_path)
    sprite.save(output_path, 'PNG')


if __name__ == '__main__':
    main()
