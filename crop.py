import argparse
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description='crop image into')
    parser.add_argument('path', type=str,
                        help='path to image file')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='directory containing frames')
    parser.add_argument('-x', '--x', type=int,
                        default=0, help='start x position')
    parser.add_argument('-y', '--y', type=int,
                        default=0, help='start y position')
    parser.add_argument('--width', type=int,
                        required=True, help='width of crop area')
    parser.add_argument('--height', type=int,
                        required=True, help='width of height of crop area')
    args = parser.parse_args()
    path = args.path
    outpath = args.output
    x = args.x
    y = args.y
    width = args.width
    height = args.height
    try:
        img = Image.open(path)
        cropped = img.crop((x, y, x + width, y + height))
        cropped.save(outpath)
    except FileNotFoundError as e:
        print('file not found, ', e)
    except Exception as e:
        print('something went wrong, ', e)


if __name__ == '__main__':
    main()
