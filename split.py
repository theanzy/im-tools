import argparse
from PIL import Image


def split(img: Image.Image, x: int, y: int) -> list[Image.Image]:
    result = []
    # height of a single piece
    height = img.height / y
    # width of a single piece
    width = img.width / x

    # start from horizontal then move down
    for r in range(y):
        # offset vertical
        start_y = r * height
        for c in range(x):
            # cut horizontal
            start_x = c * width
            frame = img.crop(
                (start_x, start_y, start_x + width, start_y + height))
            result.append(frame)
    return result


def main():
    parser = argparse.ArgumentParser(description='split image into pieces.')
    parser.add_argument('path', type=str,
                        help='path to image')
    parser.add_argument('-x', '--horizontal', type=int, required=True,
                        help='horizontal count')
    parser.add_argument('-y', '--vertical', type=int, required=True,
                        help='vertical count')
    parser.add_argument('-o', '--output', type=str, required=True,
                        help='output directory for images')
    args = parser.parse_args()

    image_path = args.path
    outpath = args.output
    x = args.horizontal
    y = args.vertical
    try:
        img = Image.open(image_path)
        images = split(img, x, y)
        for i, f in enumerate(images):
            f.save(f'{outpath}/00{i}.png', 'PNG')
    except FileNotFoundError:
        print(f'{image_path} is not a valid image')
    # except Exception as e:
    #     print('somehting went wrong', e)


if __name__ == '__main__':
    main()
