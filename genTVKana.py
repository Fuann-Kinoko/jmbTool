import json
import os
import shutil
import subprocess
from typing import Dict
from jmbStruct import stFontParam, SIChr, texStrImage, stTex, texMeta

from wand.image import Image
from wand.color import Color
from wand.font import Font

BLOCK_HEIGHT = 27

gCurX = 0
gCurY = 0
gChCnt = 0

def register(json_file_path:str) -> str:
    skipping_chars = set(" ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789%?!「」・")
    unique_chars = set()
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # 确保data是字典类型
        if not isinstance(data, dict):
            raise ValueError("JSON文件内容不是一个字典")
        # 遍历字典中的每个键值对
        for key, value in data.items():
            if isinstance(value, str):
                # 检查每个字符
                for char in value:
                    if char not in skipping_chars:
                        unique_chars.add(char)
    return "".join(unique_chars)

def print_info(st: texStrImage):
    print(st.header)
    for i in range(st.header.strPackNum):
        print(st.strpack[i])
    for i in range(st.header.strNum):
        print(st.str[i])
    for i in range(st.header.chrNum):
        print(f"[{i}] {st.chb[i]}")
    print(f"{st.tex.header.w=}, {st.tex.header.h=}, {st.tex.header.dds_size=}")
    print(f"{len(st.tex.dds)=}")
    print(st.tex.header)
    print("="*20)

def gen_char_image(char: str, width, height) -> Image:
    assert(len(char) == 1)
    img = Image(width=width*4, height=height*4, background=Color('transparent'))
    font_path = "TT_DotGothic12-M.ttf"
    img.font = Font(
        path=font_path,
        color = Color('white'),
        size = height*4
    )
    img.gravity = 'center'
    img.caption(text=char)
    OFFSET = -4
    img.roll(y=OFFSET)
    return img

def gen_default_chr(char: str, cur_x = 0, cur_y = 0) -> SIChr:
    addx = BLOCK_HEIGHT
    addw = 1
    c = SIChr()
    c.code = ord(char)
    c.code2 = ord(char)
    c.x = cur_x
    c.y = cur_y
    c.w = addx
    c.h = addx
    c.dx = 0
    c.dy = 0
    c.addx = addx
    assert addw == 1
    c.addw = b'\x01'
    return c

def Task_CharChange_TVKANA():
    gCurX = 0
    gCurY = 0
    gChCnt = 0
    fp = open("D:/SteamLibrary/steamapps/common/killer7/Readonly/Yam/CharChange/Pack/CharChange/TVKana.sti", "rb")
    assert fp.read(4) == b'STRI'
    fp.seek(0)
    strimage = texStrImage(fp)
    fp.close()
    gChCnt = strimage.header.chrNum

    print_info(strimage)

    TVKana_json = "D:/SteamLibrary/steamapps/common/killer7/Tools/jmbDump/assets/translation/TVKana.json"
    unique_chars = register(TVKana_json)
    print(len(unique_chars), unique_chars)

    canvas = Image(width=strimage.tex.header.w*4, height=(strimage.tex.header.h+len(unique_chars)*BLOCK_HEIGHT)*4, background=Color('transparent'))
    with Image(blob=strimage.tex.dds) as orig:
        canvas.composite(orig, left=0, top=0)
    gCurLineCharCnt = 0
    WIDTH_CAPACITY = 8
    gCurY = 9 * BLOCK_HEIGHT
    for ch in unique_chars:
        if gCurLineCharCnt >= WIDTH_CAPACITY:
            gCurX = 0
            gCurY += BLOCK_HEIGHT
            gCurLineCharCnt = 0
        c = gen_default_chr(ch, gCurX, gCurY)
        strimage.chb.append(c)
        c_img = gen_char_image(ch, BLOCK_HEIGHT, BLOCK_HEIGHT)
        canvas.composite(c_img, left=gCurX*4, top=gCurY*4)
        c_img.close()
        gCurX += BLOCK_HEIGHT
        gCurLineCharCnt += 1
        gChCnt += 1
    canvas.crop(0, 0, width=strimage.tex.header.w*4, height=(gCurY + BLOCK_HEIGHT)*4)
    canvas.format='png'
    canvas.save(filename="TVKana_mod.png")
    canvas.close()
    command = [
        "texconv.exe",
        "-f", "BC7_UNORM_SRGB",  # 压缩格式
        "-ft", "dds",            # 输出文件类型
        "-srgb",                 # 输入为 sRGB，输出也为 sRGB
        "-m", "1",               # 禁用 mipmap
        "-y",                    # 覆盖输出文件（不提示）
        "TVKana_mod.png",        # 输入文件
    ]
    subprocess.run(command, check=True)
    strimage_ddstex = stTex()
    fp = open("TVKana_mod.dds", 'rb')
    dds_bytes = fp.read()
    fp.close()
    dds_header = texMeta()
    dds_header.magic = b'GCT0'
    dds_header.idk = b'\x00\x00\x00\x01'
    bin_dds_img = Image(blob=dds_bytes)
    width, height = bin_dds_img.size
    bin_dds_img.close()
    dds_header.w = width // 4
    dds_header.h = height // 4
    dds_header.dds_size = len(dds_bytes)
    # 组装
    strimage_ddstex.header = dds_header
    strimage_ddstex.dds = dds_bytes
    strimage.tex = strimage_ddstex
    strimage.header.chrNum = gChCnt

    print_info(strimage)

    with open("TVKana_mod.sti", "wb") as fp:
        strimage.write(fp)
        print("write to TVKana_mod.sti")

    source_sti = r"D:/SteamLibrary/steamapps/common/killer7/Tools/jmbDump/TVKana_mod.sti"
    dest_sti   = r"D:/SteamLibrary/steamapps/common/killer7/Extracted/Yam/CharChange/Pack/CharChange/TVKana.sti"
    rsl_pack_exe = r"D:/SteamLibrary/steamapps/common/killer7/Tools/no_more_rsl/rslPack.exe"
    target_dir = r"D:/SteamLibrary/steamapps/common/killer7/Extracted/Yam/CharChange/Pack/CharChange"
    shutil.copy2(source_sti, dest_sti)
    subprocess.run([rsl_pack_exe, "--overwrite", target_dir], check=True)
    modi_rsl = r"D:/SteamLibrary/steamapps/common/killer7/Extracted/Yam/CharChange/Pack/CharChange.rsl"
    targ_rsl = r"D:/SteamLibrary/steamapps/common/killer7/Yam/CharChange/Pack/CharChange.rsl"
    shutil.copy2(modi_rsl, targ_rsl)

def Task_Menu_TVKANA():
    gCurX = 0
    gCurY = 0
    gChCnt = 0
    fp = open("D:/SteamLibrary/steamapps/common/killer7/Readonly/fonts/TVKana.sti", "rb")
    assert fp.read(4) == b'STRI'
    fp.seek(0)
    strimage = texStrImage(fp)
    fp.close()
    gChCnt = strimage.header.chrNum

    print_info(strimage)

    TVKana_Menu_json = "D:/SteamLibrary/steamapps/common/killer7/Tools/jmbDump/assets/translation/TVKana_Menu.json"
    unique_chars = register(TVKana_Menu_json)
    print(len(unique_chars), unique_chars)

    canvas = Image(width=strimage.tex.header.w*4, height=(strimage.tex.header.h+len(unique_chars)*BLOCK_HEIGHT)*4, background=Color('transparent'))
    with Image(blob=strimage.tex.dds) as orig:
        canvas.composite(orig, left=0, top=0)
    gCurLineCharCnt = 0
    WIDTH_CAPACITY = 8
    gCurY = 9 * BLOCK_HEIGHT
    for ch in unique_chars:
        if gCurLineCharCnt >= WIDTH_CAPACITY:
            gCurX = 0
            gCurY += BLOCK_HEIGHT
            gCurLineCharCnt = 0
        c = gen_default_chr(ch, gCurX, gCurY)
        strimage.chb.append(c)
        c_img = gen_char_image(ch, BLOCK_HEIGHT, BLOCK_HEIGHT)
        canvas.composite(c_img, left=gCurX*4, top=gCurY*4)
        c_img.close()
        gCurX += BLOCK_HEIGHT
        gCurLineCharCnt += 1
        gChCnt += 1
    canvas.crop(0, 0, width=strimage.tex.header.w*4, height=(gCurY + BLOCK_HEIGHT)*4)
    canvas.format='png'
    canvas.save(filename="TVKana_Menu_mod.png")
    canvas.close()
    command = [
        "texconv.exe",
        "-f", "BC7_UNORM_SRGB",  # 压缩格式
        "-ft", "dds",            # 输出文件类型
        "-srgb",                 # 输入为 sRGB，输出也为 sRGB
        "-m", "1",               # 禁用 mipmap
        "-y",                    # 覆盖输出文件（不提示）
        "TVKana_Menu_mod.png",        # 输入文件
    ]
    subprocess.run(command, check=True)
    strimage_ddstex = stTex()
    fp = open("TVKana_Menu_mod.dds", 'rb')
    dds_bytes = fp.read()
    fp.close()
    dds_header = texMeta()
    dds_header.magic = b'GCT0'
    dds_header.idk = b'\x00\x00\x00\x01'
    bin_dds_img = Image(blob=dds_bytes)
    width, height = bin_dds_img.size
    bin_dds_img.close()
    dds_header.w = width // 4
    dds_header.h = height // 4
    dds_header.dds_size = len(dds_bytes)
    # 组装
    strimage_ddstex.header = dds_header
    strimage_ddstex.dds = dds_bytes
    strimage.tex = strimage_ddstex
    strimage.header.chrNum = gChCnt

    print_info(strimage)

    with open("TVKana_Menu_mod.sti", "wb") as fp:
        strimage.write(fp)
        print("write to TVKana_Menu_mod.sti")

    source_sti = r"D:/SteamLibrary/steamapps/common/killer7/Tools/jmbDump/TVKana_Menu_mod.sti"
    dest_sti   = r"D:/SteamLibrary/steamapps/common/killer7/Extracted/fonts/TVKana.sti"
    targ_sti   = r"D:/SteamLibrary/steamapps/common/killer7/fonts/TVKana.sti"
    shutil.copy2(source_sti, dest_sti)
    shutil.copy2(source_sti, targ_sti)

if __name__ == '__main__':
    Task_CharChange_TVKANA()
    Task_Menu_TVKANA()