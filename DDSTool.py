import os
import shutil
import subprocess
import fontTool
import jmbConst
from jmbStruct import stFontParam
from wand.image import Image
from wand.display import display
from wand.color import Color

def extract(output_dir : str, dds_bytes : bytes, char_infos : list[stFontParam], scale_factor=4, should_store = False):
    """Extracts individual character images from a DDS font texture atlas.

    Processes a DDS texture containing font glyphs, cropping out each character
    based on provided fParams. Optionally saves each character as separate PNG files.

    Args:
        output_dir (str): Directory to store extracted character images (created if not exists)
        dds_bytes (bytes): Binary data of the DDS texture file
        char_infos (list[stFontParam]): List of character metadata
        scale_factor (int, optional): Multiplier for converting between DDS Canvas and fParas
            pixels. Defaults to 4 (for 4x upscaled textures).
        should_store (bool, optional): Whether to save individual character images as PNGs.
            If False, only performs bounds checking. Defaults to False.
    """
    os.makedirs(output_dir, exist_ok=True)
    char_image_cnt = 0
    with Image(blob=dds_bytes) as img:
        width, height = img.size
        print(f"DDS图像尺寸: {width}x{height}")

        for idx, char in enumerate(char_infos):
            u_phys = char.u * scale_factor
            v_phys = char.v * scale_factor
            w_phys = char.w * scale_factor
            h_phys = char.h * scale_factor
            if (u_phys + w_phys > width or
                v_phys + h_phys > height):
                print(f"Warning: 字符{idx}超出图像边界")
                continue
            char_img = img.clone()
            char_img.crop(u_phys, v_phys, width=w_phys, height=h_phys)
            char_image_cnt += 1
            if should_store:
                char_img.compression = "no"
                char_img.save(filename=f'{output_dir}/char_{idx:02d}.png')

    print(f"成功提取 {char_image_cnt} 个字符图像")

def reconstruction(
        input_dir : str,
        output_path : str,
        char_infos : list[stFontParam],
        max_width=jmbConst.JIMAKU_TEX_WIDTH*4,
        fixed_max_width = False,
        original_alignment = True
    ):
    char_images = []
    for i in range(len(char_infos)):
        img_path = os.path.join(input_dir, f"char_{i:02d}.png")
        if not os.path.exists(img_path):
            print(f"警告: 字符图片 {img_path} 不存在")
            continue
        try:
            img = Image(filename=img_path)
            char_images.append(img)
        except Exception as e:
            print(f"加载图片 {img_path} 失败: {e}")

    if not char_images:
        print("错误: 没有找到任何字符图片")
        return

    char_height = char_images[0].height  # 所有字符高度相同
    print(f"字符高度: {char_height} 像素")

    # 创建透明背景的RGBA画布
    canvas_width = max_width
    canvas_height = char_height * 32  # 初始高度足够大，最后再裁剪
    canvas = Image(width=canvas_width, height=canvas_height, background=Color('transparent'))

    current_x = 0
    current_y = 0
    current_max_width = 0
    row_count = 0

    for i, (char_img, char_info) in enumerate(zip(char_images, char_infos)):
        w = char_info.w
        h = char_info.h
        assert(w*4 == char_img.width)
        assert(h*4 == char_img.height)
        step = w
        if original_alignment and w in {35 , 28 , 21 , 47}:
            step += 1

        # 检查是否需要换行
        if current_x + step * 4 >= max_width:
            row_count += 1
            current_x = 0
            current_y += char_height

        # print(f"char[{i}] : w={char_width}, h={char_height}; u before={current_x}({info_u}), u after={current_x+char_width}; v={current_y}({info_v}); row={row_count}")
        canvas.composite(char_img, left=current_x, top=current_y)

        current_x += step * 4
        assert(current_x == char_info.u)
        assert(current_y == char_info.v)

        if current_x > current_max_width:
            current_max_width = current_x

    # 计算实际使用的画布高度
    actual_height = current_y + char_height
    actual_width = max_width if fixed_max_width else current_max_width
    print(f"canvas = {actual_width} x {actual_height}")

    # 裁剪画布到实际高度
    canvas.crop(0, 0, width=actual_width, height=actual_height)

    # 保存为DDS (BC7压缩)
    try:
        canvas.format='png'
        canvas.save(filename="temp.png")
        canvas.close()

        command = [
            "texconv.exe",
            "-f", "BC7_UNORM_SRGB",  # 压缩格式
            "-ft", "dds",            # 输出文件类型
            "-srgb",                 # 输入为 sRGB，输出也为 sRGB
            "-m", "1",               # 禁用 mipmap
            "-y",                    # 覆盖输出文件（不提示）
            "temp.png",              # 输入文件
        ]
        subprocess.run(command, check=True)
        shutil.move("temp.dds", output_path)
        os.remove("temp.png")

        print(f"\n成功重建DDS贴图: {output_path}")
        print(f"行数: {row_count + 1}")
        print(f"压缩格式: BC7 (BC7)")
    except Exception as e:
        print(f"保存DDS失败: {e}")

def gen(
    output_path: str,
    unique_chars: str,
    usage: jmbConst.JmkUsage,

    max_width: int = jmbConst.JIMAKU_TEX_WIDTH*4,
    fixed_max_width: bool = False,
    original_alignment: bool = True
    ):
    """Generates a DDS texture atlas from unique characters with font rendering.

    Creates a texture atlas containing all input characters rendered using the font tool,
    then converts it to BC7-compressed DDS format. The layout automatically wraps characters
    based on max width constraints.

    Args:
        output_path (str): Path to save the output DDS file (e.g., 'texture.dds')
        unique_chars (str): String containing unique characters to render in the atlas
        usage (JmkUsage): uses corresponding font metrics.
            1. Nameplate  (34px height).
            2. Hato(Mail) (44px height).
            3. Default    (57px height)

        max_width (int, optional): Maximum texture width in pixels. Defaults to 4x JIMAKU_TEX_WIDTH
        fixed_max_width (bool, optional):
            If True, forces output width to match max_width.
            If False, uses actual content width. Defaults to False.
        original_alignment (bool, optional):
            When True, mimics the original game's character spacing behavior which adds 1px
            extra spacing for Kanji, Kana, Numeric, and Special characters. This implementation
            tries to match the original game's (somewhat unusual) text rendering logic.

            Note: While this option exists for validation/accuracy purposes, in practice
            1. If the fparams generation is also using the simpler (not original) alignment calculation,
            there's no difference in gameplay.
            2. A simpler alignment system (where param[i+1].u = param[i].u+param[i].w)
                would be more maintainable and equally effective

            Defaults to True (a replication of original behavior).
            But recommended to be False.
    """
    match usage:
        case jmbConst.JmkUsage.Name:
            HEIGHT = 34
        case jmbConst.JmkUsage.Hato:
            HEIGHT = 44
        case _:
            HEIGHT = 57
    canvas_width = max_width
    canvas_height = HEIGHT * 4 * ((len(unique_chars) // 8)+1)

    canvas = Image(width=canvas_width, height=canvas_height, background=Color('transparent'))

    current_x = 0
    current_y = 0
    row_count = 0
    col_count = 0
    current_max_width = 0
    for char in unique_chars:
        kind = fontTool.check_kind(char)
        w = kind.get_width(usage, alpha_ch=char)
        h = kind.get_height(usage, alpha_ch=char)
        assert(h == HEIGHT)
        step = w
        if original_alignment and kind in (fontTool.FontKind.KANJI , fontTool.FontKind.KATA , fontTool.FontKind.NUM , fontTool.FontKind.SPECIAL):
            step += 1

        if current_x + step*4 >= max_width:
            row_count += 1
            col_count = 0
            current_x = 0
            current_y += HEIGHT*4

        offset_y = 0
        if False and usage == jmbConst.JmkUsage.Hato: # FIXME: is there any actual tilt?
            offset_y = - col_count

        char_img = fontTool.gen_char_image(char, usage)
        canvas.composite(char_img, left=current_x, top=current_y+offset_y)
        char_img.close()

        current_x += step*4
        col_count += 1
        if current_x > current_max_width:
            current_max_width = current_x

    actual_height = current_y + HEIGHT * 4
    actual_width = max_width if fixed_max_width else current_max_width
    print(f"canvas = {actual_width} x {actual_height}")

    canvas.crop(0, 0, width=actual_width, height=actual_height)

    try:
        canvas.format='png'
        canvas.save(filename="temp.png")
        canvas.close()

        # 使用Wand保存为DDS，BC7压缩
        command = [
            "texconv.exe",
            "-f", "BC7_UNORM_SRGB",  # 压缩格式
            "-ft", "dds",            # 输出文件类型
            "-srgb",                 # 输入为 sRGB，输出也为 sRGB
            "-m", "1",               # 禁用 mipmap
            "-y",                    # 覆盖输出文件（不提示）
            "temp.png",              # 输入文件
        ]
        subprocess.run(command, check=True)
        shutil.move("temp.dds", output_path)
        os.remove("temp.png")

        print(f"\n成功重建DDS贴图: {output_path}")
        print(f"行数: {row_count + 1}")
        print(f"压缩格式: BC7 (BC7)")
    except Exception as e:
        print(f"保存DDS失败: {e}")
        return None

def print_info(dds_bytes: bytes):
    print("DDS Size: ", len(dds_bytes))
    with Image(blob=dds_bytes) as img:
        width, height = img.size
        print(f"DDS Canvas Size: {width}x{height}")