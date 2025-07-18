import shutil
import subprocess
from jmbStruct import stFontParam, SIChr, texStrImage, stTex, texMeta

from wand.image import Image
from wand.color import Color
from wand.font import Font

gCurX = 0
gCurY = 0
gChCnt = 0

BLOCK_HEIGHT = 22

def print_info(st: texStrImage):
    print(st.header)
    for i in range(st.header.strPackNum):
        print(st.strpack[i])
    for i in range(st.header.strNum):
        print(st.str[i])
    for i in range(st.header.chrNum):
        print(st.chb[i])
    print(f"{st.tex.header.w=}, {st.tex.header.h=}, {st.tex.header.dds_size=}")
    print(f"{len(st.tex.dds)=}")
    print("="*20)

def gen_char_image(char: str, width, height) -> Image:
    assert(len(char) == 1)
    img = Image(width=width*4, height=height*4, background=Color('transparent'))
    font_path = "SourceHanSerifCN-Bold.otf"
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

# 似乎它会检查是否属于原来的？
# 例：Y7StageTitle.cpp, YK7StageTitleDat.h
# 换行的纯粹原因似乎只是因为第二行的第一个字是“及”，
# 如果把及放到fake_sjs其它地方，就会影响什么时候换行
fake_sjs = "笑顔本陣壊滅依頼及び、首領の生け捕り"       # 这个是正确版本
# fake_sjs = "笑顔本陣壊滅依頼　及び、首領の生け捕り"   # 这个反而会吞掉译文第二行第一个字
def gen_default_chr(char: str, cur_x = 0, cur_y = 0) -> SIChr:
    addx = BLOCK_HEIGHT
    addw = 1
    c = SIChr()
    c.code = ord(fake_sjs[gChCnt])
    c.code2 = ord(fake_sjs[gChCnt])
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

fp = open("D:\\SteamLibrary\\steamapps\\common\\killer7\\Readonly\\subtitle\\st00J\\st00FontJ.sti", 'rb')
assert fp.read(4) == b'STRI'
fp.seek(0)
strimage = texStrImage(fp)
fp.close()

print_info(strimage)

line1 = "笑颜总部歼灭委托"
line2 = "及首领的活捉"
assert len(line1 + line2) == 14
strimage.header.chrNum = 14
strimage.str[0].strIndex[:8] = [0,1,2,3,4,5,6,7]
strimage.str[0].strIndex[8:13] = [-1,0,0,0,0]
strimage.str[1].strIndex[:6] = [8,9,10,11,12,13]
strimage.str[1].strIndex[6:13] = [-1,0,0,0,0,0,0]

strimage.chb.clear()
canvas = Image(width=BLOCK_HEIGHT*4*10, height=BLOCK_HEIGHT*4*10, background=Color('transparent'))
usedMaxX = 0
gCurX = 0
gCurY = 0
for ch in (line1 + line2):
    if (gCurX + BLOCK_HEIGHT) >= 94:
        gCurX = 0
        gCurY += BLOCK_HEIGHT
    c = gen_default_chr(ch, gCurX, gCurY)
    strimage.chb.append(c)
    c_img = gen_char_image(ch, BLOCK_HEIGHT, BLOCK_HEIGHT)
    canvas.composite(c_img, left=gCurX*4, top=gCurY*4)
    c_img.close()
    gCurX += BLOCK_HEIGHT
    usedMaxX = max(usedMaxX, gCurX)
    gChCnt += 1
canvas_u = usedMaxX
canvas_v = gCurY + BLOCK_HEIGHT
canvas.crop(0, 0, width=canvas_u*4, height=canvas_v*4)
canvas.format='png'
canvas.save(filename="testFont.png")
canvas.close()
command = [
    "texconv.exe",
    "-f", "BC7_UNORM_SRGB",  # 压缩格式
    "-ft", "dds",            # 输出文件类型
    "-srgb",                 # 输入为 sRGB，输出也为 sRGB
    "-m", "1",               # 禁用 mipmap
    "-y",                    # 覆盖输出文件（不提示）
    "testFont.png",              # 输入文件
]
subprocess.run(command, check=True)
strimage_ddstex = stTex()
# 获取header相关内容
fp = open("testFont.dds", 'rb')
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

assert gChCnt == 14

print_info(strimage)

with open("testFont.sti", "wb") as fp:
    strimage.write(fp)
    print("write to testFont.sti")

source_sti = r"D:/SteamLibrary/steamapps/common/killer7/Tools/jmbDump/testFont.sti"
dest_sti   = r"D:/SteamLibrary/steamapps/common/killer7/Extracted/subtitle/st00J/st00FontJ.sti"
rsl_pack_exe = r"D:/SteamLibrary/steamapps/common/killer7/Tools/no_more_rsl/rslPack.exe"
target_dir = r"D:/SteamLibrary/steamapps/common/killer7/Extracted/subtitle/st00J"
shutil.copy2(source_sti, dest_sti)
subprocess.run([rsl_pack_exe, "--overwrite", target_dir], check=True)
modi_rsl = r"D:/SteamLibrary/steamapps/common/killer7/Extracted/subtitle/st00J.rsl"
targ_rsl = r"D:/SteamLibrary/steamapps/common/killer7/subtitle/st00J.rsl"
shutil.copy2(modi_rsl, targ_rsl)