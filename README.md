This library provides an in-memory interface for reading/writing subtitle-related files from the game Killer7.

Supported file formats:
- Jimaku Binary File (JMB)
- String Image (STRIMAGE)
- Texture Files (BIN)

Developed for the [k7cn](https://github.com/Fuann-Kinoko/k7cn) project.

# Related Projects
- [No-More-RSL(Timo654)](https://github.com/Timo654/No-More-RSL/)

# Requirements
- [Wand(Python Binding for ImageMagick)](https://pypi.org/project/Wand/)

# Getting Started
## JMB files
### Reading and Exploring

A JMB file consists of the following parts:
1. Metadata
2. Sentences data
3. Font parameters (defining `u;v;w;h` coordinates for each character in the atlas texture)
4. Atlas texture
5. Motion data (Japanese version only)

To read a JMB file, specify the input path and version (`JP` or `US`), then call `BaseGdat.create()`:

```python
import os
from jmbTool.jmbConst import JmkKind
from jmbTool.jmbData import BaseGdat

input_path = "some_zan_or_charageki_file.jmb"
jmb_name = os.path.basename(input_path)[:-4]

# Detect version based on filename
if 'J' in jmb_name or ('Movie' in input_path and 'E' not in jmb_name):
    kind = JmkKind.JA
else:
    kind = JmkKind.US

jmb = BaseGdat.create(input_path, kind)
```

Explore the JMB file structure:

```python
from pprint import pprint
from jmbTool.typeUtils import _TYPE_is_US, _TYPE_is_JA

print("\n==== MetaData ====")
print(jmb.meta)

print("\n==== Sentence Info ====")
for i in range(jmb.meta.sentence_num):
    if _TYPE_is_JA(jmb):
        print(f"st {i}")
        for jmk_idx, jmk in enumerate(jmb.sentences[i].jimaku_list):
            print(f"\t [{jmk_idx}] char_data {jmk.char_data}")
    elif _TYPE_is_US(jmb):
        print(f"st {i} char_data {jmb.sentences[i].char_data}")
    else:
        assert False, "unreachable"

print("\n==== Font Params ====")
for idx, fParam in enumerate(jmb.fParams):
    print(f"[{idx}] {fParam}")

print("\n==== Export DDS Texture ====")
jmb.tex.dump("test.dds")
```

### Extracting Individual Characters

Extract characters from the texture atlas using the font parameters:

```python
from wand.image import Image

SCALE_FACTOR = 4    # most jmb textures have been upscaled, but the font params have not been adjusted
output_dir = "atlas_chars"
os.makedirs(output_dir, exist_ok=True)
char_cnt = 0

with Image(blob=jmb.tex.dds) as img:
    width, height = img.size
    print(f"Atlas texture dimensions: {width}x{height}")

    for idx, char in enumerate(jmb.fParams):
        u_phys = char.u * SCALE_FACTOR
        v_phys = char.v * SCALE_FACTOR
        w_phys = char.w * SCALE_FACTOR
        h_phys = char.h * SCALE_FACTOR

        # Validate coordinates
        if (u_phys + w_phys > width or v_phys + h_phys > height):
            print(f"Warning: Character {idx} has out-of-bounds coordinates: {char}")
            continue

        char_img = img.clone()
        char_img.crop(u_phys, v_phys, width=w_phys, height=h_phys)
        char_cnt += 1
        char_img.compression = "no"
        char_img.save(filename=f'{output_dir}/char_{idx:02d}.png')
```

### Generate Preview Images for Each Sentence

Once you have extracted the individual characters, you can generate preview images for each sentence based on control codes in the sentence:

```python
from wand.color import Color
from jmbTool.jmbStruct import stFontParam, stJimaku # stJimaku = stJimaku_US | stJimaku_JA
from jmbTool import jmbUtils
from jmbTool.jmbNumeric import S16_BE

extracted_chars_dir = "atlas_chars"
preview_dir = "preview"
SCALE_FACTOR = 4

def save_preview(target_path: str, jmk: stJimaku, fParams: list[stFontParam], extracted_chars_dir: str):
    SATSU_FLAG      = S16_BE("8000")
    SHI_FLAG        = S16_BE("7000")
    SPACE_H_FLAG    = S16_BE("fffd")
    SPACE_Z_FLAG    = S16_BE("fffc")
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    char_data = jmbUtils.display_char_data(jmk.char_data)
    FONT_HEIGHT = max(param_i.h for param_i in fParams)

    if len(char_data) == 0:
        img = Image(width=35, height=FONT_HEIGHT*SCALE_FACTOR, background=Color('black'))
        img.format='png'
        img.save(filename=target_path)
        img.close()
        return

    canvas = Image(width=70*SCALE_FACTOR*len(char_data), height=FONT_HEIGHT*SCALE_FACTOR, background=Color('black'))
    current_x = 0
    for ctl in char_data:
        ctl_s16 = S16_BE(ctl)
        if (ctl_s16 == SPACE_H_FLAG or   # Half-Width Space
            ctl_s16 == SPACE_Z_FLAG or   # Full-Width Space
           (ctl_s16 & S16_BE("ff00")) == S16_BE("ff00")): # Controller Related Buttons
            current_x += 21*SCALE_FACTOR
            continue

        if  (ctl_s16 & SHI_FLAG) != S16_BE("0000") or \
            (ctl_s16 & SATSU_FLAG) != S16_BE("0000"):
            mask = S16_BE("0fff")
        else:
            mask = S16_BE("ffff")
        index = (mask & ctl_s16).to_int()
        with Image(filename=f"{extracted_chars_dir}/char_{index:02d}.png") as char_img:
            step = (char_img.width // SCALE_FACTOR) + 1
            canvas.composite(char_img, left=current_x, top=0, operator='atop')
            current_x += step * SCALE_FACTOR

    canvas.crop(0, 0, width=current_x + 16, height=FONT_HEIGHT * SCALE_FACTOR)
    canvas.format='png'
    canvas.save(filename=target_path)
    canvas.close()

for i in range(jmb.meta.sentence_num):
    print(f"generating preview for sentence {i}")
    if _TYPE_is_JA(jmb):
        sent = jmb.sentences[i]
        for jmk_idx, jmk in enumerate(sent.jimaku_list):
            if not jmk.valid():
                break
            target_path = f"{preview_dir}/JA_sent{i}/{jmk_idx:02d}"
            save_preview(target_path+".png", jmk, jmb.fParams, extracted_chars_dir)
    elif _TYPE_is_US(jmb):
        sent = jmb.sentences[i]
        if not sent.valid():
            break
        target_path = f"{preview_dir}/US_sent{i}"
        save_preview(target_path+".png", sent, jmb.fParams, extracted_chars_dir)

```

### Saving Updated JMB File

If you've made changes to the JMB file, for example, delaying every subtitle by 1 second, you can save the updated JMB file to test the results:

```python
if _TYPE_is_JA(jmb):
    for oneSentence in jmb.sentences:
        for jmk in oneSentence.jimaku_list:
            jmk.wait += 4800 # +1 second; wait/disp_time is stored as s32 integer,
                             # representing rounded value of (time_in_seconds * 4800)
elif _TYPE_is_US(jmb):
    for jmk in jmb.sentences:
        jmk.wait += 4800
else:
    assert False, "unreachable"

jmb.write_to_file("new.jmb")

```

### Translation: Updating Control Codes and Texture

This library provides a basic, non-flexible atlas generation method. If you are working on translation, you may need to implement a more flexible solution to handle various font types. However, the built-in generator allows for a quick test.

For a more complex example, please refer to the [k7cn](https://github.com/Fuann-Kinoko/k7cn/blob/master/DDSTool.py) project for an example of CJK atlas generation.

#### Overview

Assuming you have translated subtitles with new control codes and a generated texture:
```
text:
    This is a test
control codes:
    0 -> T
    1 -> h
    2 -> i
    3 -> s
    4 -> a
    5 -> t
    6 -> e
valid sentence data:
    0 1 2 3 -4 2 3 -4 4 5 6 3 5
    (-4 = full-width space; -3 = half-width space)
font params:
    prepare your own
```

The following code shows how to update the JMB file and save the translated version:

```python
text = "This is a test"
codes = [0, 1, 2, 3, -4, 2, 3, -4, 4, 5, 6, 3, 5]
atlas_path = "new.dds"
if _TYPE_is_JA(jmb):
    # Update font parameters
    jmb.fParams = ... # Replace with your updated font parameters
    # Update sentence data
    oneSentence_0 = jmb.sentences[0]
    jmk_0 = oneSentence_0.jimaku_list[0]
    jmk_0.overwrite_ctl(codes)
    # Update atlas texture
    jmb.reimport_tex(atlas_path)
    jmb.recalculate_meta() # Recalculate header since some sizes have changed
elif _TYPE_is_US(jmb):
    # Update font parameters
    jmb.fParams = ... # Replace with your updated font parameters
    # Update sentence data
    jmk_0 = jmb.sentences[0]
    jmk_0.overwrite_ctl(codes)
    # Update atlas texture
    jmb.reimport_tex(atlas_path)
    jmb.recalculate_meta() # Recalculate header since some sizes have changed
else:
    assert False, "unreachable"

jmb.write_to_file("new.jmb") # Save translated version
```

#### Built-in Atlas Generation

Below is a quick demo of generating an atlas from translated text using the integrated generator and updating the JMB file:

```python
from jmbTool import atlasGeneration, jmbData, jmbConst

INPUT_PATH = "killer7\\ReadOnly\\CharaGeki\\00010101\\00010101\\00010101.jmb"
CHAR_HEIGHT     = 24
FONT_SIZE       = 68
FONT_PATH       = "SourceHanSerifCN-Bold.otf"
SCALE_FACTOR    = 4
jmb = jmbData.BaseGdat.create(INPUT_PATH, jmbConst.JmkKind.US)

text = [
    "Это　я,　ты　уже　на　месте?",
    "Ты　имеешь　в　виду　эту　дыру?",
    "Там　они　все　тусуются.",
    "Наша　информация　говорит,　что　их　там　14.",
    "И　всех　надо　охотиться?",
    "Не,　оставь　одного　в　живых,",
    "чтобы　мы　могли　спросить,",
    "кто　их　босс.",
    "Что　ещё　мне　нужно　знать?",
    "Да　нет,　в　общем-то,　ты　поймёшь,　когда　их　увидишь,",
    "они,　э-э...　другие.",
    "Будет　сделано.",
    "Пусть　Господь　улыбнётся...",
    "...а　Дьявол　смилуется.",
]
# text = [
#     "Aquí　estoy.　¿Ya　llegaste?",
#     "¿Te　refieres　a　este　maldito　agujero?",
#     "Ahí　es　donde　todos　se　reúnen.",
#     "Nuestra　información　indica　que　son　catorce.",
#     "¿Y　todos　están　listos　para　cazar?",
#     "No,　deja　uno　con　vida",
#     "para　preguntarle",
#     "quién　es　su　jefe.",
#     "¿Algo　más　que　deba　saber?",
#     "Na,　en　realidad　no.　Los　reconocerás　al　verlos,",
#     "son,　eh,　diferentes.",
#     "De　acuerdo.",
#     "Que　el　Señor　sonría...",
#     "...y　el　Diablo　tenga　piedad."
# ]
text_flatten = "".join(text)
ctl2char_lookup, char2ctl_lookup, unique_chars = atlasGeneration.char_register(text_flatten)

canvas, fontParams = atlasGeneration.gen_atlas_US(
    FONT_PATH, unique_chars, CHAR_HEIGHT, FONT_SIZE, SCALE_FACTOR,
    debug=False
)
canvas.save(filename='atlas.png')

command = [
    "texconv.exe",
    "-f", "BC7_UNORM_SRGB",
    "-ft", "dds",
    "-srgb",
    "-m", "1",
    "-y",
    "atlas.png",
]
import subprocess
subprocess.run(command, check=True)

jmb.fParams = fontParams
assert len(text) == jmb.meta.sentence_num
for idx, jmk in enumerate(jmb.sentences):
    text_sentence = text[idx]
    text_codes = [char2ctl_lookup[c] for c in text_sentence]
    jmk.overwrite_ctl(text_codes)
jmb.reimport_tex("atlas.dds")
jmb.recalculate_meta()

jmb.write_to_file("00010101.jmb")
```

## BIN files

Note: Some STRIMAGE files also use the .BIN extension, but they can be distinguished by checking the file's magic numbers. This section specifically covers .BIN files used for storing textures.

### Export DDS Texture from .BIN Files

```python
from wand.image import Image
from jmbTool.jmbStruct import stTex

filename = "file.BIN"
with open(filename, 'rb') as fp:
    tex = stTex(fp)
    print("tex header =", tex.header)

    # Export raw DDS texture
    tex.dump("dump.dds")

    # Convert and export as PNG
    with Image(blob=dds_bytes) as img:
        img.format = 'png'
        img.save("dump.png")
```

### Reimporting DDS Texture to .BIN Files

```python
from wand.image import Image
from jmbTool.jmbStruct import stTex

SCALE_FACTOR = 4 # Adjust based on texture scaling (use 1 for non-upscaled textures)
updated_dds_path = "updated.dds"
original_bin_path = "file.BIN"
# Read original BIN file
with open(original_bin_path, 'rb') as fp:
    tex = stTex(fp)
# Update texture data
with open(updated_dds_path, 'rb') as fp_dds:
    tex.dds = fp_dds.read()
    with Image(blob=tex.dds) as img:
        img_width, img_height = img.size
    tex.header.w = img_width // SCALE_FACTOR
    tex.header.h = img_height // SCALE_FACTOR
    tex.header.dds_size = len(tex.dds)
# Write modified BIN file
with open("new.BIN", 'wb') as bfp:
    tex.write(bfp)
```

## STRIMAGE files
TODO: examples

# Notes
## Texture Compression
Most subtitle textures use `BC7` compression following recent updates. However, the ImageMagick library currently only supports `BC5` compression. For conversion, it is recommended to use [texconv](https://github.com/microsoft/DirectXTex).