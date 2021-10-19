import io
import aiohttp
from typing import Tuple
from PIL import Image, ImageDraw, ImageFont, ImageFilter



class Io:

    def __init__(self):
        pass

    @staticmethod
    def draw(size: Tuple, color: str = None):

        """
        :param size: dimension of the image to be created
        :param color: color of the image (hex string or hex)
        :return: image in form BytesIO object
        """

        color = 0x36393f if color is None else color
        new_image = Image.new("RGB", size, color=color)
        buff = io.BytesIO()
        new_image.save(buff, 'png')
        buff.seek(0)
        return buff

    @classmethod
    async def fetch(cls, url: str):

        """
        :param url: url of the image to be fetched
        :return: image form the url in the form of BytesIO Object
        """

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                resp = await response.read()
                return io.BytesIO(resp)


    @classmethod
    def save(cls, _byte, name:str):

        """
        :param _byte: image of BytesIO form
        :param str name: name of the image with extension
        :return: None
        """

        img = Image.open(_byte)
        img.save(name)
        return None


class Canvas:

    def __init__(self, size: Tuple, color: str = None):

        """
        :param size: Tuple of width and height of Canvas
        :param color: Hex or String of the desired color-code
        """

        color = 0x36393f if color is None else color
        size = size if size is not None and len(size) == 2 else None
        card = Image.new("RGB", size, color=color)
        buff = io.BytesIO()
        card.save(buff, 'png')
        buff.seek(0)
        self.width = size[0]
        self.height = size[1]
        self.output = buff



    def set_background(self, _byte = None, _path: str = None, _blur:bool = False):

        """
        :param _byte: bytesio form of the image
        :param _path: path where the image is stored locally
        :param _blur: to make the background blurry
        :return: None
        """

        canvas = Image.open(self.output)
        size = canvas.size
        if _path is not None and _byte is None:
            bg = Image.open(_path)
        elif _byte is not None and _path is None:
            bg = Image.open(_byte)
        else:
            raise Exception("Use either _path or _byte")

        if bg is not None:
            _bg = bg.resize(size)
            if _blur:
                buff = io.BytesIO()
                _bg_blur = _bg.filter(ImageFilter.BLUR)
                _bg_blur.save(buff, 'png')
                buff.seek(0)
                self.output = buff

            else:
                buff = io.BytesIO()
                _bg.save(buff, 'png')
                buff.seek(0)
                self.output = buff

        else:
            raise TypeError("Image can not be NoneType")



    def add_image(self, _path: str = None, _byte = None, resize: Tuple = None, crop: Tuple = None,
                  position: Tuple = None):

        """
        :param str _path: path where the image is stored locally
        :param _byte: bytesio form of the image
        :param Tuple resize: tuple of length 2 (width, height) to resize the image
        :param Tuple crop: tuple of length 4 (left, top, right, bottom) to crop the image
        :param Tuple position: tuple of coordinate (x,y) to where the image will be added into canvas
        :raises Exception: if _path and _byte both are available
        :raises TypeError: if NoneType is passed as image
        :raises Exception: if crop and resize both are available
        :return: None
        """

        canvas = Image.open(self.output)
        if _path is not None and _byte is None:
            img = Image.open(_path)
        elif _byte is not None and _path is None:
            img = Image.open(_byte)
        else:
            raise Exception("Use either _path or _byte")

        if img is not None:

            if resize is not None and crop is None:
                auto_align = ((self.width - resize[0]) // 2, (self.height - resize[1]) // 2)
                manual_align = position
                offset = auto_align if position is None else manual_align
                _img = img.resize(resize, resample=0)
                Image.Image.paste(canvas, _img, offset)
                buff = io.BytesIO()
                canvas.save(buff, 'png')
                buff.seek(0)
                self.output = buff
            elif crop is not None and resize is None:
                _img = img.crop(crop)
                dim = _img.size
                auto_align = ((self.width - dim[0]) // 2, (self.height - dim[1]) // 2)
                manual_align = position
                offset = auto_align if position is None else manual_align
                Image.Image.paste(canvas, _img, offset)
                buff = io.BytesIO()
                canvas.save(buff, 'png')
                buff.seek(0)
                self.output = buff
            elif crop is None and resize is None:
                size = img.size
                auto_align = ((self.width - size[0]) // 2, (self.height - size[1]) // 2)
                manual_align = (position[0], position[1])
                offset = auto_align if position is None else manual_align
                Image.Image.paste(canvas, img, offset)
                buff = io.BytesIO()
                canvas.save(buff, 'png')
                buff.seek(0)
                self.output = buff
            else:
                raise Exception('Use either Resize or Crop')
        else:
            raise TypeError('Image can not be NoneType')



    def add_round_image(self, _path: str = None, _byte = None, resize: Tuple = None, crop: Tuple = None,
                        position: Tuple = None):

        """
        :param str _path: path where the image is stored locally
        :param  _byte: bytesio form of the image
        :param Tuple resize: tuple of length 2 (width, height) to resize the image
        :param Tuple crop: tuple of length 4 (left, top, right, bottom) to crop the image
        :param Tuple position: tuple of coordinate (x,y) to where the image will be added into canvas
        :raises Exception: if _path and _byte both are available
        :raises TypeError: if NoneType is passed as image
        :raises Exception: if crop and resize both are available
        :return: None
        """

        canvas = Image.open(self.output)
        if _path is not None and _byte is None:
            img = Image.open(_path)
        elif _byte is not None and _path is None:
            img = Image.open(_byte)
        else:
            img = None

        if img is not None:

            if resize is not None and crop is None:
                main = img.resize(resize)
                mask = Image.new("L", main.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.pieslice([(0, 0), main.size], 0, 360, fill=255, outline="white")
                dim = main.size
                auto_align = ((self.width - dim[0]) // 2, (self.height - dim[1]) // 2)
                manual_align = position
                offset = auto_align if position is None else manual_align
                canvas.paste(main, offset, mask)
                buff = io.BytesIO()
                canvas.save(buff, 'png')
                buff.seek(0)
                self.output = buff
            elif crop is not None and resize is None:
                main = img.crop(crop)
                mask = Image.new("L", main.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.pieslice([(0, 0), main.size], 0, 360, fill=255, outline="white")
                dim = main.size
                auto_align = ((self.width - dim[0]) // 2, (self.height - dim[1]) // 2)
                manual_align = position
                offset = auto_align if position is None else manual_align
                canvas.paste(main, offset, mask)
                buff = io.BytesIO()
                canvas.save(buff, 'png')
                buff.seek(0)
                self.output = buff
            elif crop is None and resize is None:
                main = img
                mask = Image.new("L", main.size, 0)
                draw = ImageDraw.Draw(mask)
                draw.pieslice([(0, 0), main.size], 0, 360, fill=255, outline="white")
                dim = main.size
                auto_align = ((self.width - dim[0]) // 2, (self.height - dim[1]) // 2)
                manual_align = position
                offset = auto_align if position is None else manual_align
                canvas.paste(main, offset, mask)
                buff = io.BytesIO()
                canvas.save(buff, 'png')
                buff.seek(0)
                self.output = buff
            else:
                raise Exception('Use either Resize or Crop')

        else:
            raise TypeError('Image can not be NoneType')



    def add_text(self, text: str, auto_align:bool, size: float = None, color: str = None,
                 position: Tuple = None):

        """
        :param str text: text to be added to the image
        :param bool auto_align: for horizontal text alignment
        :param int size: size of text
        :param str color: name of color or color code
        :param Tuple position: tuple of coordinate (x,y) to where the text will be added into canvas
        :return: None
        """

        canvas = Image.open(self.output)
        draw = ImageDraw.Draw(canvas)
        text = text
        size = 20 if size is None else size
        color = 'white' if color is None else color

        font = ImageFont.truetype(font = 'sans.ttf', size=size)

        text_width, text_height = draw.textsize(text, font=font)

        def align(auto:bool, pos):
            if auto is True and pos is None:
                return (self.width - text_width) // 2, (self.height - text_height) // 2

            elif auto is True and pos is not None:
                return (self.width - text_width) // 2, position[1]

            elif auto is False and pos is None:
                return (self.width - text_width) // 2, (self.height - text_height) // 2

            elif auto is False and pos is not None:
                return pos

        draw.text(align(auto_align, position), text, fill=color, font=font)
        buff = io.BytesIO()
        canvas.save(buff, 'png')
        buff.seek(0)
        self.output = buff

    @property
    def show(self):

        """
        Shows the Canvas object. Use to preview the canvas or image
        :return: None
        """

        image = Image.open(self.output)
        image.show()
        return None


    def save(self, name:str):

        """
        :param name: name of the image with extension
        :return: None
        """

        img = Image.open(self.output)
        img.save(name)