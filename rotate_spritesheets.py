import argparse
from PIL import Image


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
        frames[0].save('temp.png')
        sprite = merge_frames_x(frames)
        sprite.save(outpath, 'PNG')
    except FileNotFoundError as e:
        print('file not found, ', e)
    except Exception as e:
        print('something went wrong, ', e)


if __name__ == '__main__':
    main()
