from PIL import Image
import os
import argparse


max_sprites_row = 3.0
frames = []


def save_image():
    return


def merge_frames_x(frames: list[Image.Image]) -> Image.Image:

    tile_width = max([f.width for f in frames])
    tile_height = max([f.height for f in frames])
    spritesheet_width = tile_width * len(frames)
    spritesheet_height = tile_height
    spritesheet = Image.new("RGBA", (int(spritesheet_width), int(spritesheet_height)))
    for i, f in enumerate(frames):
        left = int(i * tile_width + tile_width / 2 - f.width / 2)
        right = left + tile_width
        top = 0
        top = int(tile_height / 2 - f.height / 2)
        bottom = top + tile_height
        box = (
            left,
            top,
            right,
            bottom,
        )
        cut_frame = f.crop((0, 0, tile_width, tile_height))
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
    spritesheet = merge_frames_x(frames)
    spritesheet.save(output_path, "PNG")
    for f in frames:
        f.close()


if __name__ == "__main__":
    main()
