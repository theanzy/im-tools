from PIL import Image
import os
import math
import time
import argparse


max_sprites_row = 3.0
frames = []


def save_image():
    return


def merge_frames(frames: list[Image.Image]) -> Image.Image:

    tile_width = frames[0].width
    tile_height = frames[0].height
    spritesheet_width = tile_width * len(frames)
    spritesheet_height = tile_height
    spritesheet = Image.new("RGBA", (int(spritesheet_width), int(spritesheet_height)))
    for i, frame in enumerate(frames):
        left = i * tile_width
        right = left + tile_width
        top = 0
        bottom = top + tile_height
        box = (
            left,
            top,
            right,
            bottom,
        )
        cut_frame = frame.crop((0, 0, tile_width, tile_height))
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
        except Exception:
            print(f"{filepath} is not a valid image")
    return frames


def main():
    parser = argparse.ArgumentParser(description="Images to spritesheet.")
    parser.add_argument("path", type=str, help="directory containing frames")
    parser.add_argument(
        "-o", "--output", type=str, required=True, help="directory containing frames"
    )
    args = parser.parse_args()
    output_path = args.output
    print(output_path, args.path)
    frames = get_frames(args.path)
    spritesheet = merge_frames(frames)
    spritesheet.save(output_path, "PNG")
    for f in frames:
        f.close()


if __name__ == "__main__":
    main()
