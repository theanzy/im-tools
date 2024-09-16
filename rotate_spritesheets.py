import argparse
from PIL import Image

from merge_x import merge_frames_x




def main():
    parser = argparse.ArgumentParser(description='rotate spritesheet image')
    parser.add_argument('path', type=str,
                        help='path to image file')
    parser.add_argument('-n', '--nframe', type=int, required=True,
                        help='number of frames')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='output path of image')
    parser.add_argument('-d', '--degree', type=int, required=True,
                        help='degree to rotate')
    args = parser.parse_args()
    path = args.path
    outpath = args.output
    nframe = args.nframe

    frames: list[Image.Image] = []
    try:
        img = Image.open(path)
        iwidth = img.width / nframe
        iheight = img.height
        degree = args.degree
        for i in range(0, nframe):
            i_frame = img.crop((i * iwidth, 0, i * iwidth + iwidth, iheight))
            i_frame = i_frame.rotate(degree, Image.NEAREST, expand=1)
            frames.append(i_frame)
        sprite = merge_frames_x(frames)
        sprite.save(outpath, 'PNG')
    except FileNotFoundError as e:
        print('file not found, ', e)
    except Exception as e:
        print('something went wrong, ', e)


if __name__ == '__main__':
    main()
