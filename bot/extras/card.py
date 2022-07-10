import io
import PIL
import asyncio
import aiohttp
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter


class Canvas:

    @staticmethod
    def draw(size: Tuple, color: str = None):
        color = 0x36393f if not color else color
        image = Image.new("RGB", size, color=color)
        buff = io.BytesIO()
        image.save(buff, 'png')
        buff.seek(0)
        return buff

    def __init__(self, size: Tuple, color: str = None):
        color = 0x36393f if color is None else color
        size = size if len(size) >= 2 else None
        card = Image.new("RGB", size, color=color)
        buff = io.BytesIO()
        card.save(buff, 'png')
        buff.seek(0)
        self.width = size[0]
        self.height = size[1]
        self.output = buff

    def set_background(self, fp, blur: bool = False):
        buff = io.BytesIO()
        canvas = Image.open(self.output)
        size = canvas.size
        bg = Image.open(fp).convert('RGB').resize(size)
        if blur:
            blurred = bg.filter(ImageFilter.BLUR)
            blurred.save(buff, 'png')
        else:
            bg.save(buff, 'png')
        buff.seek(0)
        self.output = buff

    def add_image(
            self,
            *,
            fp,
            resize: Tuple = None,
            crop: Tuple = None,
            position: Tuple = None
    ):
        img = Image.open(fp)
        canvas = Image.open(self.output)
        if resize and not crop:
            img_ = img.resize(resize, resample=0)
            auto = ((self.width - resize[0]) // 2, (self.height - resize[1]) // 2)
            offset = auto if not position else position
        elif crop and not resize:
            img_ = img.crop(crop)
            dim = img_.size
            auto = ((self.width - dim[0]) // 2, (self.height - dim[1]) // 2)
            offset = auto if not position else position
        elif crop is None and resize is None:
            size = img.size
            auto = ((self.width - size[0]) // 2, (self.height - size[1]) // 2)
            offset = auto if not position else position
        else:
            raise Exception('Use either Resize or Crop')

        Image.Image.paste(canvas, img, offset)
        buff = io.BytesIO()
        canvas.save(buff, 'png')
        buff.seek(0)
        self.output = buff

    def add_round_image(
            self,
            *,
            fp,
            resize: Tuple = None,
            crop: Tuple = None,
            position: Tuple = None
    ):
        canvas = Image.open(self.output)
        img = Image.open(fp)
        if resize is not None and crop is None:
            main = img.resize(resize)

        elif crop is not None and resize is None:
            main = img.crop(crop)

        elif crop is None and resize is None:
            main = img
        else:
            raise RuntimeError('Use either Resize or Crop')

        mask = Image.new("L", main.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.pieslice(((0, 0), main.size), 0, 360, fill=255, outline="white")
        dim = main.size
        auto_align = ((self.width - dim[0]) // 2, (self.height - dim[1]) // 2)
        manual_align = position
        offset = auto_align if position is None else manual_align
        canvas.paste(main, offset, mask)
        buff = io.BytesIO()
        canvas.save(buff, 'png')
        buff.seek(0)
        self.output = buff

    def add_text(
            self,
            text: str,
            *,
            align: bool,
            size: float = None,
            color: str = None,
            position: Tuple = None
    ):
        canvas = Image.open(self.output)
        draw = ImageDraw.Draw(canvas)
        text = text
        size = 20 if size is None else size
        color = 'white' if color is None else color
        font = ImageFont.truetype(font='bot/extras/sans.ttf', size=size)
        text_width, text_height = draw.textsize(text, font=font)

        def aligner(auto: bool, pos: Tuple):
            if auto and not pos:
                return (self.width - text_width) // 2, (self.height - text_height) // 2
            elif auto and pos:
                return (self.width - text_width) // 2, position[1]
            elif not auto and not pos:
                return (self.width - text_width) // 2, (self.height - text_height) // 2
            elif not auto and pos:
                return pos

        draw.text(aligner(align, position), text, fill=color, font=font)
        buff = io.BytesIO()
        canvas.save(buff, 'png')
        buff.seek(0)
        self.output = buff
