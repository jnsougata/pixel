import io
import textwrap
from typing import Tuple, Union, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter


MISSING = object()
Number = Union[int, float]
Path = Union[str, bytes, io.BytesIO]
Color = Union[str, Tuple[int, int, int], float, int]


class Canvas:

    def __init__(
        self,
        width: int = 2048,
        height: int = 1080,
        color: Color = 'white',
    ):
        self.fonts = []
        self.width, self.height = width, height
        self.ctx = Image.new("RGB", (width, height), color=color)

    def load_fonts(self, *fonts: Path):
        for font in fonts:
            self.fonts.append(font)

    def set_background(self, path: Path, *, blur_level: int = MISSING):
        bg = Image.open(path)
        if bg.mode != 'RGBA':
            bg = bg.convert('RGBA')
        if blur_level is not MISSING:
            bg = bg.filter(ImageFilter.GaussianBlur(radius=blur_level))
        self.ctx.paste(bg.resize((self.width, self.height), resample=Image.LANCZOS), (0, 0, self.width, self.height))

    def draw_line(
        self,
        coords: List[Tuple[Number, Number]],
        *,
        color: Color = 'black',
        width: int = 1,
    ):
        draw = ImageDraw.Draw(self.ctx)
        if len(coords) < 2:
            raise ValueError('You must provide at least 2 coordinates')
        draw.line(coords, fill=color, width=width)

    def draw_image(
        self,
        path: Path,
        position_left: int = MISSING,
        position_top: int = MISSING,
        *,
        rotate: int = MISSING,
        resize_x: int = MISSING,
        resize_y: int = MISSING,
        crop_left: int = MISSING,
        crop_top: int = MISSING,
        crop_right: int = MISSING,
        crop_bottom: int = MISSING,
        blur_level: int = MISSING,
    ):
        img = Image.open(path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        if rotate is not MISSING:
            img = img.rotate(rotate)
        if blur_level is not MISSING:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_level))
        if resize_x is not MISSING and resize_y is MISSING:
            img = img.resize((resize_x, img.size[1]))
        elif resize_x is MISSING and resize_y is not MISSING:
            img = img.resize((img.size[0], resize_y))
        elif resize_x is not MISSING and resize_y is not MISSING:
            img = img.resize((resize_x, resize_y))
        cl = 0 if crop_left is MISSING else crop_left
        ct = 0 if crop_top is MISSING else crop_top
        cr = img.width if crop_right is MISSING else crop_right
        cb = img.height if crop_bottom is MISSING else crop_bottom
        img = img.crop((cl, ct, cr, cb))
        if position_left is MISSING and position_top is not MISSING:
            offset = (self.width - img.width) // 2, position_top
        elif position_left is not MISSING and position_top is MISSING:
            offset = position_left, (self.height - img.height) // 2
        elif position_left is MISSING and position_top is MISSING:
            offset = (self.width - img.width) // 2, (self.height - img.height) // 2
        else:
            offset = position_left, position_top
        self.ctx.paste(img, box=offset)

    def draw_round_image(
        self,
        path: Path,
        position_left: int = MISSING,
        position_top: int = MISSING,
        *,
        rotate: int = MISSING,
        resize_x: int = MISSING,
        resize_y: int = MISSING,
        crop_left: int = MISSING,
        crop_top: int = MISSING,
        crop_right: int = MISSING,
        crop_bottom: int = MISSING,
        blur_level: int = MISSING,
    ):
        img = Image.open(path)
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        if rotate is not MISSING:
            img = img.rotate(rotate)
        if blur_level is not MISSING:
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_level))
        if img.width != img.height:
            crop_val = (max(img.size) - min(img.size)) // 2
            if img.height > img.width:
                img = img.crop((0, crop_val, img.width, img.height - crop_val))
            else:
                img = img.crop((crop_val, 0, img.width - crop_val, img.height))
        if resize_x is not MISSING and resize_y is MISSING:
            img = img.resize((resize_x, img.size[1]))
        elif resize_x is MISSING and resize_y is not MISSING:
            img = img.resize((img.size[0], resize_y))
        elif resize_x is not MISSING and resize_y is not MISSING:
            img = img.resize((resize_x, resize_y))
        cl = 0 if crop_left is MISSING else crop_left
        ct = 0 if crop_top is MISSING else crop_top
        cr = img.width if crop_right is MISSING else crop_right
        cb = img.height if crop_bottom is MISSING else crop_bottom
        img = img.crop((cl, ct, cr, cb))
        if position_left is MISSING and position_top is not MISSING:
            offset = (self.width - img.width) // 2, position_top
        elif position_left is not MISSING and position_top is MISSING:
            offset = position_left, (self.height - img.height) // 2
        elif position_left is MISSING and position_top is MISSING:
            offset = (self.width - img.width) // 2, (self.height - img.height) // 2
        else:
            offset = position_left, position_top
        img = img.crop((cl, ct, cr, cb))
        mask = Image.new("L", img.size, 0)
        cursor = ImageDraw.Draw(mask)
        cursor.pieslice(((0, 0), img.size), 0, 360, fill=255, outline="white")
        self.ctx.paste(img, offset, mask)

    def draw_text(
            self,
            text: str,
            *,
            top: float = MISSING,
            left: float = MISSING,
            line_space: float = 0.0,
            outline: int = MISSING,
            outline_color: Color = 'black',
            shadow: int = MISSING,
            shadow_color: Color = 'black',
            font_index: int = 0,
            font_size: int = 30,
            font_color: Color = 'black',
    ):
        if text == '':
            raise ValueError('text cannot be empty')
        if len(self.fonts) == 0:
            raise ValueError('fonts cannot be empty if text is used. use `load_font(...)` to add fonts')
        if font_index >= len(self.fonts):
            raise ValueError('font_index cannot be greater than the number of fonts added to the canvas')
        font = ImageFont.truetype(self.fonts[font_index], size=font_size)
        cursor = ImageDraw.Draw(self.ctx)
        text_width, text_height = cursor.textsize(text, font=font, spacing=line_space)
        if left is MISSING and top is not MISSING:
            left_wrap = 0
            offset = (self.width - text_width) / 2, top
        elif left is not MISSING and top is MISSING:
            left_wrap = left
            offset = left, (self.height - text_height) / 2
        elif left is MISSING and top is MISSING:
            left_wrap = 0
            offset = (self.width - text_width) / 2, (self.height - text_height) / 2
        else:
            left_wrap = left
            offset = left, top
        if (len(text) * (font_size / 2)) - left_wrap > self.width:
            width = int(self.width / (font_size / 1.15))
            text = textwrap.fill(text, width=width)

        if shadow is not MISSING:
            shadow_offset = offset[0] - shadow, offset[1] - shadow
            cursor.text(shadow_offset, text, font=font, fill=shadow_color, spacing=line_space)

        if outline is not MISSING:
            cursor.text(
                offset, text, font=font, fill=font_color,
                spacing=line_space, stroke_width=outline, stroke_fill=outline_color)
        else:
            cursor.text(offset, text, font=font, fill=font_color, spacing=line_space)

    def read(self) -> io.BytesIO:
        return io.BytesIO(self.ctx.tobytes())

    def show(self):
        self.ctx.show()

    def save(self, path: Path):
        self.ctx.save(path)

    @staticmethod
    def get_accent(path: Path) -> Color:
        img = Image.open(path).convert('RGBA')
        r, g, b, _ = img.resize((1, 1), resample=0).getpixel((0, 0))
        return f'#{r:02x}{g:02x}{b:02x}'

    @property
    def accent(self) -> Color:
        copied_canvas = self.ctx.copy().convert('RGBA')
        r, g, b, _ = copied_canvas.resize((1, 1), resample=0).getpixel((0, 0))
        return f'#{r:02x}{g:02x}{b:02x}'
