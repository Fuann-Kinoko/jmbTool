# Current Status

Currently, CJK text for CharaGeki can be processed successfully, but it's unclear how to configure them for EU/US versions.

This means only `{stage}J.jmb` files are guaranteed to be correctly handled.

TODO: Documentation

# Related Projects

- [No-More-RSL(Timo654)](https://github.com/Timo654/No-More-RSL/)
- [DirectXTex(BC7 Compression support)](https://github.com/microsoft/DirectXTex)

# Requirements

- Fonts:
  - ヒラギノ明朝体 W4 - W8
  - Source Han Serif
  - Modify the font path in `fontTool.py` as needed
- [Wand(Python Binding for ImageMagick)](https://pypi.org/project/Wand/)

- Place [texconv](https://github.com/microsoft/DirectXTex/releases/) in the working directory

# Usage

Entry Point:

(reference paths are hardcoded in the script, so please read the code first)

```sh
python tasks.py
```
