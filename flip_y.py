
from PIL import Image, ImageOps
import argparse

from merge_x import merge_frames_x


def main():
    parser = argparse.ArgumentParser(
        description='flip spritesheet vertically.')
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
        mirrored = ImageOps.flip(i_frame)
        frames.append(mirrored)

    sprite = merge_frames_x(frames)
    sprite.save(output_path, 'PNG')


if __name__ == '__main__':
    main()
