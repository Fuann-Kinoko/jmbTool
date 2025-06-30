from enum import Enum, auto
import os
from typing import Union
from jmbStruct import stFontParam, stJimaku
import jmbUtils

from wand.image import Image
from wand.color import Color
from wand.font import Font
from wand.display import display
from wand.drawing import Drawing

Font_SourceHan = "SourceHanSerifCN-Bold.otf"
Font_HiraginoMincho = "HiraginoMinCho-W6.ttc"
SATSU_FLAG = 0x8000
SHI_FLAG = 0x7000

BODY_FACE_SCALE_SIZE = 57
NAME_FACE_SCALE_SIZE = 34
BODY_WIDTH_SCALE_SIZE = 35
NAME_WIDTH_SCALE_SIZE = 28

DEFAULT_FACE_SIZE = 142         # scale = 7.5
KATA_FACE_SIZE = 112            # scale = 6
KANA_FACE_SIZE = 104            # scale = 5.5
SPECIAL_FACE_SIZE = 188         # scale = 10
NUM_FACE_SIZE = 142             # scale = 7.5
QUOTE_FACE_SIZE = 142           # scale = 7.5

DEFAULT_HEIGHT = 57

DEFAULT_WIDTH  = 35
KATA_WIDTH  = 28
KANA_WIDTH = 26
SPECIAL_WIDTH = 47
NUM_WIDTH = 21
QUOTE_WIDTH = 19

class FontKind(Enum):
    KANJI = auto()
    KATA = auto()
    KANA = auto()
    SPECIAL = auto()
    NUM = auto()
    QUOTE = auto()

    def get_face_size(self, for_name = False) -> int:
        scale:float = 1.0
        if for_name:
            scale = NAME_FACE_SCALE_SIZE / BODY_FACE_SCALE_SIZE
        match self:
            case FontKind.KANA:
                return int(scale * KANA_FACE_SIZE)
            case FontKind.KATA:
                return int(scale * KATA_FACE_SIZE)
            case FontKind.KANJI:
                return int(scale * DEFAULT_FACE_SIZE)
            case FontKind.NUM:
                return int(scale * NUM_FACE_SIZE)
            case FontKind.QUOTE:
                return int(scale * QUOTE_FACE_SIZE)
            case FontKind.SPECIAL:
                return int(scale * SPECIAL_FACE_SIZE)
            case _:
                NotImplemented

    def get_width(self, for_name = False) -> int:
        scale:float = 1.0
        if for_name:
            scale = NAME_FACE_SCALE_SIZE / BODY_FACE_SCALE_SIZE
        match self:
            case FontKind.KANA:
                return int(scale * KANA_WIDTH)
            case FontKind.KATA:
                return int(scale * KATA_WIDTH)
            case FontKind.KANJI:
                return int(scale * DEFAULT_WIDTH)
            case FontKind.NUM:
                return int(scale * NUM_WIDTH)
            case FontKind.QUOTE:
                return int(scale * QUOTE_WIDTH)
            case FontKind.SPECIAL:
                return int(scale * SPECIAL_WIDTH)
            case _:
                NotImplemented

    def get_height(self, for_name = False) -> int:
        scale:float = 1.0
        if for_name:
            scale = NAME_FACE_SCALE_SIZE / BODY_FACE_SCALE_SIZE
        return int(scale * DEFAULT_HEIGHT)


def check_kind(char: str) -> FontKind:
    if len(char) != 1:
        raise ValueError("Input must be a single character")
    code = ord(char)
    if char == " " or char.isdigit():
        return FontKind.NUM
    elif char == "“" or char == "”":
        return FontKind.QUOTE
    # ひらがな（平假名）
    elif (0x3040 <= code <= 0x309F) or (char in {"、", "。", "，", "．", "・", "～", "…", "‥"}):
        return FontKind.KANA
    # カタカナ（片假名）
    elif (char not in {"ー", "―", "‐"}) and (0x30A0 <= code <= 0x30FF):
        return FontKind.KATA
    # 特殊字符（如「殺」「死」）
    elif char == "殺" or char == "死":
        return FontKind.SPECIAL
    # 默认认为是汉字
    else:
        return FontKind.KANJI

def to_signed_16bit(n: int) -> int:
    n = n & 0xFFFF
    return n if n < 0x8000 else n - 0x10000

def register(input: str) -> tuple[dict[int, str], dict[str, int], str]:
    counter = 0
    unique_jmk = ""
    ctl2char_dict = {}
    char2ctl_dict = {}
    ctl2char_dict[-3] = " "
    char2ctl_dict[" "] = -3
    ctl2char_dict[-4] = "　"
    char2ctl_dict["　"] = -4

    for char in input:
        if char == "、" or char == "。":
            char2ctl_dict[char] = -3
            continue
        if char == " " or char == "　":
            continue
        if char not in char2ctl_dict:
            unique_jmk += char
            if char == "殺":
                signed = to_signed_16bit(counter | SATSU_FLAG)
                ctl2char_dict[signed] = char
                char2ctl_dict[char] = signed
            elif char == "死":
                signed = to_signed_16bit(counter | SHI_FLAG)
                ctl2char_dict[signed] = char
                char2ctl_dict[char] = signed
            else:
                ctl2char_dict[counter] = char
                char2ctl_dict[char] = counter
            counter += 1
    return ctl2char_dict, char2ctl_dict, unique_jmk


def gen_char_image(char: str, info: stFontParam = None, for_name = False) -> Image:
    assert(len(char) == 1)
    kind = check_kind(char)
    if info is not None:
        img = Image(width=info.w*4, height=info.h*4, background=Color('transparent'))
    else:
        img = Image(width=kind.get_width(for_name)*4, height=kind.get_height(for_name)*4, background=Color('transparent'))

    if kind == FontKind.QUOTE:
        if char == "“":
            img = Image(filename="assets/chars/JA_quote_open.png")
        elif char == "”":
            img = Image(filename="assets/chars/JA_quote_close.png")
        else:
            assert False, "Unreachable"
        return img

    if kind == FontKind.KANJI and char != "？":
        font_path = Font_SourceHan
    else:
        font_path = Font_HiraginoMincho

    img.font = Font(
        path=font_path,
        color = Color('white'),
        # stroke_color=Color('#d4d4d4'),
        # stroke_width=1,
        size = kind.get_face_size(for_name)
    )
    img.gravity = 'center'

    img.caption(text=char)

    if font_path is Font_SourceHan:
        OFFSET = -10 if for_name else -16
        img.roll(y=OFFSET)

    return img

def save_preview_jimaku(
        save_path: str,
        jimaku: stJimaku,
        ctl2char_lookup: dict[int, str] = None,
        fParams: list[stFontParam] = None,
        provided_chars_dir : str = None,
        for_name = False,
        original_alignment = True
    ):
    """Generates and saves a preview image of subtitle text (jimaku) using either character generation
    or pre-extracted character images.

    This function supports two modes of operation:
    1. Character generation mode (when `ctl2char_lookup` is provided)
    2. Pre-extracted character mode (when `fParams` and `provided_chars_dir` are provided)

    Args:
        save_path (str): Path to save the output preview image (PNG format)
        jimaku (stJimaku): Subtitle data structure containing character control codes
        ctl2char_lookup (dict[int, str], optional): Mapping of control codes to actual characters.
            Required for character generation mode.
        fParams (list[stFontParam], optional): List of font parameters for pre-extracted characters.
            Required for pre-extracted mode.
        provided_chars_dir (str, optional): Directory containing pre-extracted character images.
            Required for pre-extracted mode.
        for_name (bool, optional): If True, uses nameplate font settings. Defaults to False.
        original_alignment (bool, optional): If True, tries to mimic original game's character spacing
            behavior (adds 1px for certain character types, which is confusing and hard to predict).
            Defaults to True. But recommended to be False.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    should_gen_char : bool = (ctl2char_lookup is not None and fParams is None and provided_chars_dir is None)

    HEIGHT = NAME_FACE_SCALE_SIZE if for_name else DEFAULT_HEIGHT
    char_data = jmbUtils.display_char_data(jimaku.char_data)
    canvas = Image(width=35*4*2*len(char_data), height=HEIGHT*4, background=Color('black'))

    current_x = 0
    for i, ctl in enumerate(char_data):
        if should_gen_char:
            char = ctl2char_lookup[ctl]
            kind = check_kind(char)
            char_info = stFontParam(u=0,v=0,w=kind.get_width(for_name),h=kind.get_height(for_name))
            char_img = gen_char_image(char, char_info, for_name)
            step = kind.get_width(for_name)
            if original_alignment and kind in (FontKind.KANJI , FontKind.KATA , FontKind.NUM , FontKind.SPECIAL):
                step += 1
        else:
            if ctl == -3:
                char_img = gen_char_image(" ")
                step = 21
            elif ctl == -4:
                char_img = gen_char_image("　")
                step = 21
            else:
                mask = 0x0fff if ((ctl & SHI_FLAG) or (ctl & SATSU_FLAG)) else 0xffff
                index = ctl & mask
                char_info = fParams[index]
                char_img = Image(filename=f"{provided_chars_dir}/char_{index:02d}.png")
                step = (char_img.width // 4)+1
        # print(f"ctl = {ctl}; char = {char}; Kind = {kind};\tparams = {char_info}")

        canvas.composite(char_img, left=current_x, top=0, operator='atop')
        char_img.close()
        current_x += step*4

    if should_gen_char:
        canvas.crop(0, 0, width=current_x + 16, height=57*4)
    else:
        canvas.crop(0, 0, width=current_x + 16, height=fParams[0].h*4)
    canvas.format='png'
    canvas.save(filename=save_path)
    canvas.close()

def save_char_image(save_path: str, char: str, info: stFontParam = None, for_name = False):
    img = gen_char_image(char, info, for_name)
    img.save(filename=save_path)
    img.close()

def genFParams(
    unique_chars : str,
    max_width = 512,
    for_name = False,
    original_alignment = True
) -> list[stFontParam]:
    """Generates a list of font parameters (stFontParam) for character atlas layout.

    Calculates texture coordinates and dimensions for each character in a virtual texture atlas,
    automatically handling line wrapping when characters exceed max_width.

    Args:
        unique_chars (str): String containing unique characters to be laid out in the atlas
        max_width (int, optional): Maximum width of the virtual texture in pixels.
            Characters will wrap to new line when exceeding this width. Defaults to 512.
        for_name (bool, optional): If True, uses nameplate font metrics (34px height).
            If False, uses standard font metrics (57px height). Defaults to False.
        original_alignment (bool, optional): If True, adds 1px spacing to certain character types
            (Kanji, Katakana, Numeric, Special) to mimic original game behavior. You don't need
            this if the DDS texture isn't the original one.

            Note: While this option exists for validation/accuracy purposes, in practice
            1. If the DDS generation is also using the simpler (not original) alignment calculation,
            there's no difference in gameplay.
            2. A simpler alignment system (where param[i+1].u = param[i].u+param[i].w)
                would be more maintainable and equally effective

            Defaults to True.
            But recommended to be False.

    Returns:
        list[stFontParam]: List of font parameters
    """
    ret_list : list[stFontParam] = []
    HEIGHT = 34 if for_name else 57
    u = 0
    v = 0
    row_count = 0
    for char in unique_chars:
        kind = check_kind(char)
        w = kind.get_width(for_name)
        h = kind.get_height(for_name)
        step = w
        if original_alignment and kind in (FontKind.KANJI , FontKind.KATA , FontKind.NUM , FontKind.SPECIAL):
            step += 1

        if u + step >= max_width:
            row_count += 1
            u = 0
            v += HEIGHT

        param = stFontParam(u=u,v=v,w=w,h=h)
        ret_list.append(param)

        u += step

    return ret_list
