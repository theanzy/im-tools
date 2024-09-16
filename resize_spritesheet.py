import argparse
from PIL import Image

from merge_x import merge_frames_x




def main():
    parser = argparse.ArgumentParser(description='resize spritesheet image')
    parser.add_argument('path', type=str,
                        help='path to image file')
    parser.add_argument('-n', '--nframe', type=int, required=True,
                        help='number of frames')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='output path of image')
    parser.add_argument('-x', '--width', type=int, required=True,
                        help='new width of a single frame')
    parser.add_argument('-y', '--height', type=int, required=True,
                        help='new height of a single frame')
    args = parser.parse_args()
    path = args.path
    outpath = args.output
    nframe = args.nframe
    width = args.width
    height = args.height

    try:
        frames: list[Image.Image] = []
        img = Image.open(path)
        iwidth = img.width / nframe
        iheight = img.height
        for i in range(0, nframe):
            i_frame = img.crop((i * iwidth, 0, i * iwidth + iwidth, iheight))
            left = int((width - iwidth) / 2)
            top = int((height - iheight) / 2)
            right = int(left + iwidth)
            bottom = int(top + iheight)
            box = (left, top, right, bottom)

            newframe = Image.new('RGBA', (int(width), int(height)))
            newframe.paste(i_frame, box)
            frames.append(newframe)
        sprite = merge_frames_x(frames)
        sprite.save(outpath, 'PNG')
    except FileNotFoundError as e:
        print('file not found, ', e)


if __name__ == '__main__':
    main()
