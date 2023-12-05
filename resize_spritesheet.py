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
