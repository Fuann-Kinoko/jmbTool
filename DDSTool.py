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

def reconstruction(input_dir : str, output_path : str, char_infos : list[stFontParam], max_width=jmbConst.JIMAKU_TEX_WIDTH*4, fixed_max_width: bool = False):
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
    canvas_height = char_height * 10  # 初始高度足够大，最后再裁剪
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
        if w in {35 , 28 , 21 , 47}:
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

def gen(output_path: str, unique_chars: str, max_width: int = jmbConst.JIMAKU_TEX_WIDTH*4, fixed_max_width: bool = False, for_name: bool = False):
    HEIGHT = 34 if for_name else 57
    canvas_width = max_width
    canvas_height = HEIGHT * 4 * 10

    canvas = Image(width=canvas_width, height=canvas_height, background=Color('transparent'))

    current_x = 0
    current_y = 0
    row_count = 0
    current_max_width = 0
    for char in unique_chars:
        kind = fontTool.check_kind(char)
        w = kind.get_width(for_name)
        h = kind.get_height(for_name)
        assert(h == HEIGHT)
        step = w
        if kind in (fontTool.FontKind.KANJI , fontTool.FontKind.KATA , fontTool.FontKind.NUM , fontTool.FontKind.SPECIAL):
            step += 1

        if current_x + step*4 >= max_width:
            row_count += 1
            current_x = 0
            current_y += HEIGHT*4

        char_img = fontTool.gen_char_image(char, for_name=for_name)
        canvas.composite(char_img, left=current_x, top=current_y)
        char_img.close()

        current_x += step*4
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