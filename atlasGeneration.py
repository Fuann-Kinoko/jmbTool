from .jmbNumeric import S16_BE
from .jmbStruct import stFontParam
from . import jmbConst
from wand.image import Image
from wand.color import Color
from wand.font import Font
from wand.display import display
from wand.drawing import Drawing

def char_register(input: str) -> tuple[dict[int, str], dict[str, int], str]:
    """
    Register unique characters from input text, create control code mappings.

    Processes input text to identify unique characters and creates bidirectional mappings
    between characters and control codes. Handles special characters and sequences.

    Args:
        input_text: Input string containing text to process

    Returns:
        Tuple containing:
        - ctl2char_dict: Mapping from control codes to characters
        - char2ctl_dict: Mapping from characters to control codes
        - unique_jmk: String containing unique characters in order of appearance

    Raises:
        AssertionError: If '@' sequences are malformed
    """
    counter = 0
    unique_jmk = ""
    ctl2char_dict = {}
    char2ctl_dict = {}
    ctl2char_dict[-3] = " "
    char2ctl_dict[" "] = -3
    ctl2char_dict[-4] = "　"
    char2ctl_dict["　"] = -4

    i = 0
    while i < len(input):
        char = input[i]

        # Handle @a / @b / ... sequences
        if char == '@':
            assert i + 2 < len(input)
            assert input[i+1].isalnum() and input[i+2].isalnum()
            i += 3  # Skip both @ and the following character
            continue

        if char == "、" or char == "。":
            char2ctl_dict[char] = -3
            i += 1
            continue

        if char == " " or char == "　":
            i += 1
            continue

        if char not in char2ctl_dict:
            unique_jmk += char
            if char == "殺":
                counter_s16 = S16_BE(counter)
                signed = (counter_s16 | jmbConst.SATSU_FLAG).to_int()
                ctl2char_dict[signed] = char
                char2ctl_dict[char] = signed
            elif char == "死":
                counter_s16 = S16_BE(counter)
                signed = (counter_s16 | jmbConst.SHI_FLAG).to_int()
                ctl2char_dict[signed] = char
                char2ctl_dict[char] = signed
            else:
                ctl2char_dict[counter] = char
                char2ctl_dict[char] = counter
            counter += 1
        i += 1

    return ctl2char_dict, char2ctl_dict, unique_jmk


def gen_char_image_US(char: str, font_size: int, font_path: str, debug: bool = False) -> Image:
    """
    Generate a single character image with proper metrics and cropping.

    Creates an image containing the specified character rendered with the given font,
    automatically cropped to the character's bounding box.

    Args:
        char: Single character to render
        font_size: Font size in pixels
        font_path: Path to font file
        debug: If True, adds a red bounding box for visualization

    Returns:
        Wand Image object containing the rendered character

    Raises:
        AssertionError: If input is not a single character
    """
    assert len(char) == 1, f"Please input single character: {char}"
    img = Image(width=font_size*16, height=font_size*16, background=Color('transparent'))

    img.font = Font(
        path=font_path,
        color = Color('white'),
        size = font_size
    )

    with Drawing() as draw:
        draw.font = font_path
        draw.font_size = img.font_size
        metrics = draw.get_font_metrics(img, char)
        text_width = int(metrics.text_width)
        text_height = int(metrics.ascender - metrics.descender)
        x_offset = 0
        y_offset = int(metrics.ascender)
        draw.text(x_offset, y_offset, char)
        draw(img)

    img.crop(0, 0, width=text_width, height=text_height)
    # bounding box indicator
    if debug:
        with Drawing() as draw:
            draw.stroke_color = Color('red')
            draw.stroke_width = 1
            draw.fill_color = Color('transparent')
            draw.rectangle(left=0.5, top=0.5,
                            right=img.width-1.5,
                            bottom=img.height-1.5)
            draw(img)

    return img

def gen_atlas_US(
    font_path: str,
    unique_chars: str,
    original_char_height: int,
    scaled_font_size: int,
    scale_factor: int,

    max_width: int = jmbConst.JIMAKU_TEX_WIDTH,
    debug: bool = False
    ) -> tuple[Image, list[stFontParam]]:
    """
    Generate a texture atlas containing all unique characters.

    Creates a packed texture atlas with characters arranged, and calculates
    font parameters for each character's position and dimensions in the atlas.

    Args:
        font_path: Path to font file
        unique_chars: String containing unique characters to include
        original_char_height: Target character height before upscaling
        scaled_font_size: Font size for rendering
        scale_factor: Scaling factor
        max_width: Maximum width of the atlas texture
        debug: Enable debug visualization for character images (red border)

    Returns:
        Tuple containing:
        - canvas: Image object containing the packed character atlas
        - fontParams: List of stFontParam objects with character positioning data

    Raises:
        AssertionError: If generated character height doesn't match expected scaled height
    """

    ORI_HEIGHT = original_char_height
    PHY_HEIGHT = ORI_HEIGHT * scale_factor
    ORI_MAX_WIDTH = max_width
    PHY_MAX_WIDTH = ORI_MAX_WIDTH * scale_factor

    canvas_width = PHY_MAX_WIDTH
    canvas_height = PHY_HEIGHT * ((len(unique_chars) // 8)+1)
    canvas = Image(width=canvas_width, height=canvas_height, background=Color('transparent'))

    phy_current_x = 0
    phy_current_y = 0
    row_count = 0
    col_count = 0
    phy_current_max_width = 0
    fontParams : list[stFontParam] = []

    FUNC_PADDING = lambda x: ((x + scale_factor - 1) // scale_factor) * scale_factor

    for char in unique_chars:
        char_img = gen_char_image_US(char, scaled_font_size, font_path, debug)
        phy_char_w, phy_char_h = char_img.size
        assert phy_char_h // scale_factor == original_char_height, \
            f"Character height validation failed: {phy_char_h}px // {scale_factor} = {phy_char_h // scale_factor}, " \
            f"expected {original_char_height}. Ensure font size [{scaled_font_size}] produces " \
            f"height around [{original_char_height * scale_factor}px] when scaled."

        if phy_current_x + phy_char_w >= PHY_MAX_WIDTH:
            phy_current_x = 0
            phy_current_y += PHY_HEIGHT
            row_count += 1
            col_count = 0

        canvas.composite(char_img, left=phy_current_x, top=phy_current_y)
        char_img.close()
        fontParams.append(stFontParam(
            u=phy_current_x // scale_factor,
            v=phy_current_y // scale_factor,
            w=phy_char_w    // scale_factor,
            h=phy_char_h    // scale_factor,
        ))

        phy_current_x = FUNC_PADDING(phy_current_x + phy_char_w)
        col_count += 1
        phy_current_max_width = max(phy_current_max_width, phy_current_x)

    actual_height = phy_current_y + PHY_HEIGHT
    actual_width = FUNC_PADDING(phy_current_max_width)
    canvas.crop(0, 0, width=actual_width, height=actual_height)

    return canvas, fontParams