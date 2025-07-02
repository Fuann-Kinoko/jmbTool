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

The `.BIN` file can be interpreted as a `stTex` struct (72-byte DDS header + DDS texture data), though this hasn't been thoroughly tested.

# Notes

## Translation

Typically, control codes are dynamically regenerated because their character mappings depend on when they first appear in the text stream.

However, certain special characters have to be manually coded.

```json
"暴君で@0aを使い─"
```

In this case, the sequence `@0a` is interpreted as the control code `FF 0A` (big endian), regardless of its position in the text.

For this particular control code, it represents `SPACE` key for keyboard, or to say, `R Trigger` in gamepad.