import functools
from typing import Union
from . import jmbConst
from . import jmbUtils

import struct

def checkSize(_func=None, *, struct_size_attr="STRUCT_SIZE"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, fp, *args, **kwargs):
            before = fp.tell()
            result = func(self, fp, *args, **kwargs)
            after = fp.tell()
            struct_size = getattr(self, struct_size_attr)
            assert after - before == struct_size, (
                f"Size mismatch in {func.__name__}: "
                f"expected {struct_size}, got {after - before}"
            )
            return result
        return wrapper
    if _func is None:
        return decorator
    else:
        return decorator(_func)

def read_c_string(b):
    # 找到第一个 \x00 的位置，截断后面的内容
    null_pos = b.find(b'\x00')
    if null_pos == -1:
        return b.decode('ascii', errors='ignore')
    else:
        return b[:null_pos].decode('ascii', errors='ignore')
def write_c_string(s, length):
    encoded = s.encode('ascii') if s else b''
    # 如果太长截断
    if len(encoded) >= length:
        return encoded[:length-1] + b'\x00'  # 确保最后一个字节是 \x00
    else:
        # 填充 \x00 和 \xcd
        padding = bytes([0xCD] * (length - len(encoded) - 1))
        return encoded + b'\x00' + padding

class EndianHandler:
    def __init__(self, big_endian=False):
        self.endian_char = '>' if big_endian else '<'
    def unpack(self, fmt, data):
        return struct.unpack(f'{self.endian_char}{fmt}', data)
    def pack(self, fmt, value):
        return struct.pack(f'{self.endian_char}{fmt}', value)
    def unpack_array(self, fmt, count, data):
        return struct.unpack(f'{self.endian_char}{count}{fmt}', data)
    def pack_array(self, fmt, values):
        count = len(values)
        return struct.pack(f'{self.endian_char}{count}{fmt}', *values)

class MetaData_US:
    def __init__(self, fp = None, bigEndian = False):
        self.sentence_num : int = 0                 # s16
        self.char_num : int = 0                     # s16
        self.sentence_offset : int = 0              # u32
        self.char_offset : int = 0                  # u32
        self.tex_offset : int = 0                   # u32
        self.__big_endian = bigEndian

        if fp is not None:
            self.read(fp)

    def read(self, fp):
        handler = EndianHandler(self.__big_endian)
        self.sentence_num = handler.unpack('h', fp.read(2))[0]      # s16
        self.char_num = handler.unpack('h', fp.read(2))[0]          # s16
        self.sentence_offset = handler.unpack('I', fp.read(4))[0]   # u32
        self.char_offset = handler.unpack('I', fp.read(4))[0]       # u32
        self.tex_offset = handler.unpack('I', fp.read(4))[0]        # u32

    def write(self, fp):
        handler = EndianHandler(self.__big_endian)
        fp.write(handler.pack('h', self.sentence_num))
        fp.write(handler.pack('h', self.char_num))
        fp.write(handler.pack('I', self.sentence_offset))
        fp.write(handler.pack('I', self.char_offset))
        fp.write(handler.pack('I', self.tex_offset))

    def dump(self, filename):
        with open(filename, 'wb') as f:
            self.write(f)

    def __repr__(self):
        return (
            f"MetaData_US(jimaku_num={self.sentence_num}, "
            f"char_num={self.char_num}, "
            f"jimaku_offset={self.sentence_offset}, "
            f"char_offset={self.char_offset}, "
            f"tex_offset={self.tex_offset}, "
        )

class MetaData_JA:
    def __init__(self, fp = None, bigEndian = False):
        self.sentence_num : int = 0                 # s16
        self.char_num : int = 0                     # s16
        self.sentence_offset : int = 0              # u32
        self.char_offset : int = 0                  # u32
        self.tex_offset : int = 0                   # u32
        self.s_motion_offset : int = 0              # u32
        self.s_motion_size_tbl : list[int] = []     # u32[] NOTE: 不考虑tbl，大小至少为20
        self.__big_endian = bigEndian
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        handler = EndianHandler(self.__big_endian)
        self.sentence_num = handler.unpack('h', fp.read(2))[0]      # s16
        self.char_num = handler.unpack('h', fp.read(2))[0]          # s16
        self.sentence_offset = handler.unpack('I', fp.read(4))[0]   # u32
        self.char_offset = handler.unpack('I', fp.read(4))[0]       # u32
        self.tex_offset = handler.unpack('I', fp.read(4))[0]        # u32
        self.s_motion_offset = handler.unpack('I', fp.read(4))[0]   # u32
        self.s_motion_size_tbl = list(handler.unpack_array(         # u32[]
            'I', self.sentence_num, fp.read(4 * self.sentence_num)
        ))

    def write(self, fp):
        handler = EndianHandler(self.__big_endian)
        fp.write(handler.pack('h', self.sentence_num))
        fp.write(handler.pack('h', self.char_num))
        fp.write(handler.pack('I', self.sentence_offset))
        fp.write(handler.pack('I', self.char_offset))
        fp.write(handler.pack('I', self.tex_offset))
        fp.write(handler.pack('I', self.s_motion_offset))
        if self.sentence_num > 0:
            fp.write(handler.pack_array('I', self.s_motion_size_tbl))

    def dump(self, filename):
        with open(filename, 'wb') as f:
            self.write(f)

    def __repr__(self):
        return (
            f"MetaData(sentence_num={self.sentence_num}, "
            f"char_num={self.char_num}, "
            f"sentence_offset={self.sentence_offset}, "
            f"char_offset={self.char_offset}, "
            f"tex_offset={self.tex_offset}, "
            f"s_motion_offset={self.s_motion_offset}, "
            f"s_motion_size_tbl={self.s_motion_size_tbl})"
        )

class stInfo:
    def __init__(self, fp = None, bigEndian = False):
        self.STRUCT_SIZE = 76
        self.wait = 0            # s32
        self.hps_file = ''       # （FILE_LENGTH bytes）
        self.mth_file = ''       # （FILE_LENGTH bytes）
        self.back_locate = 0     # s16
        self.countinue = 0       # s16
        self.key = 0             # s16
        self.padding = b''
        self.__big_endian = bigEndian
        if fp is not None:
            self.read(fp)

    @checkSize
    def read(self, fp):
        handler = EndianHandler(self.__big_endian)
        self.wait = handler.unpack('i', fp.read(4))[0]         # s32
        self.hps_file = read_c_string(fp.read(jmbConst.FILE_LENGTH))
        self.mth_file = read_c_string(fp.read(jmbConst.FILE_LENGTH))
        self.back_locate = handler.unpack('h', fp.read(2))[0]  # s16
        self.countinue = handler.unpack('h', fp.read(2))[0]    # s16
        self.key = handler.unpack('h', fp.read(2))[0]          # s16
        self.padding = fp.read(2) # NOTE: 4-byte alignment padding for struct

    @checkSize
    def write(self, fp):
        handler = EndianHandler(self.__big_endian)
        fp.write(handler.pack('i', self.wait))             # s32
        fp.write(write_c_string(self.hps_file, jmbConst.FILE_LENGTH))
        fp.write(write_c_string(self.mth_file, jmbConst.FILE_LENGTH))
        fp.write(handler.pack('h', self.back_locate))      # s16
        fp.write(handler.pack('h', self.countinue))        # s16
        fp.write(handler.pack('h', self.key))              # s16
        fp.write(self.padding) # NOTE: alignment padding for struct

    def dump(self, filename):
        with open(filename, 'wb') as f:
            self.write(f)

    def __repr__(self):
        return (f"stInfo(wait={self.wait}, hps_file='{self.hps_file}', "
                f"mth_file='{self.mth_file}', "
                f"back_locate={self.back_locate}, countinue={self.countinue}, key={self.key}, padding={self.padding})")

class stRubiDat:
    def __init__(self, fp=None, bigEndian = False):
        self.STRUCT_SIZE = 22
        self.from_num : int = -1                # s8
        self.to_num : int = -1                  # s8
        self.char_id : list[int] = []           # s16[jmbConst.JIMAKU_RUBI_MAX]
        self.__big_endian = bigEndian
        if fp is not None:
            self.read(fp)

    @checkSize
    def read(self, fp):
        handler = EndianHandler(self.__big_endian)
        self.from_num = handler.unpack('b', fp.read(1))[0]       # s8
        self.to_num = handler.unpack('b', fp.read(1))[0]         # s8
        self.char_id = list(handler.unpack_array(
            'h', jmbConst.JIMAKU_RUBI_MAX, fp.read(2 * jmbConst.JIMAKU_RUBI_MAX)
        ))

    @checkSize
    def write(self, fp):
        handler = EndianHandler(self.__big_endian)
        fp.write(handler.pack('b', self.from_num))   # s8
        fp.write(handler.pack('b', self.to_num))     # s8
        fp.write(handler.pack_array('h', self.char_id))

    def dump(self, fp):
        raise NotImplementedError

    def clear(self):
        self.from_num = -1
        self.to_num = -1
        self.char_id = [-1] * jmbConst.JIMAKU_RUBI_MAX

    def __repr__(self):
        if self.from_num != -1 and self.to_num != -1:
            valid_rubis = [num for num in self.char_id if num != -1]
            return f"stRubiDat({self.from_num}->{self.to_num}, {valid_rubis})"
        else:
            return f""

class stJimaku_US:
    def __init__(self, fp = None, bigEndian = False):
        self.STRUCT_SIZE = 264
        self.wait = 0                               # s32
        self.disp_time = 0                          # s32
        self.char_data : list[int] = []             # s16[jmbConst.US_JIMAKU_CHAR_MAX] (2 * 128 = 256)
        self.__big_endian = bigEndian

        if fp is not None:
            self.read(fp)

    def valid(self) -> bool:
        return self.char_data[0] != -1

    def valid_len(self) -> int:
        if not self.valid():
            return 0
        try:
            return self.char_data.index(-2)
        except ValueError:
            return 0

    def overwrite_ctl(self, new_ctls: list[int]):
        assert len(new_ctls) > 0, "new control codes should not be empty"
        needs_padding : bool = not (-2 in new_ctls)
        if needs_padding:
            assert len(new_ctls) < jmbConst.US_JIMAKU_CHAR_MAX, "length of control codes should not exceed the maximum length (128)"
            self.char_data = new_ctls
            self.char_data.append(-2)
            while len(self.char_data) < jmbConst.US_JIMAKU_CHAR_MAX:
                self.char_data.append(-1)
        else:
            assert len(new_ctls) == jmbConst.US_JIMAKU_CHAR_MAX, "length of control codes should be the same as the maximum length (128)"
            self.char_data = new_ctls

    @checkSize
    def read(self, fp):
        handler = EndianHandler(self.__big_endian)
        self.wait = handler.unpack('i', fp.read(4))[0]          # s32
        self.disp_time = handler.unpack('i', fp.read(4))[0]     # s32
        self.char_data = list(handler.unpack_array(
            'h', jmbConst.US_JIMAKU_CHAR_MAX, fp.read(2 * jmbConst.US_JIMAKU_CHAR_MAX)
        ))

    @checkSize
    def write(self, fp):
        handler = EndianHandler(self.__big_endian)
        fp.write(handler.pack('i', self.wait))             # s32
        fp.write(handler.pack('i', self.disp_time))        # s32
        fp.write(handler.pack_array('h', self.char_data))

    def __repr__(self):
        char_str = ''.join([chr(c) if c > 0 else f'[{c}]' for c in self.char_data[:8]])
        return (f"stJimaku_US(wait={self.wait}, disp_time={self.disp_time}, "
                f"char_data='{char_str}...')")

class stJimaku_JA:
    def __init__(self, fp = None, bigEndian = False):
        self.STRUCT_SIZE = 424
        self.wait = 0             # s32
        self.disp_time = 0        # s32
        self.char_data : list[int]  = []            # s16[jmbConst.JIMAKU_CHAR_MAX] (2 * 32 = 64)
        self.rubi_data : list[stRubiDat] = []       # stRubiDat[jmbConst.JIMAKU_RUBI_DAT_MAX] (22 * 16 = 352)
        self.__big_endian = bigEndian
        if fp is not None:
            self.read(fp)

    def valid(self) -> bool:
        return self.char_data[0] != -1

    def valid_len(self) -> int:
        if not self.valid():
            return 0
        try:
            return self.char_data.index(-2)
        except ValueError:
            return 0

    def overwrite_ctl(self, new_ctls: list[int]):
        assert len(new_ctls) > 0, "new control codes should not be empty"
        needs_padding : bool = not (-2 in new_ctls)
        if needs_padding:
            assert len(new_ctls) < jmbConst.JIMAKU_CHAR_MAX, "length of control codes should not exceed the maximum length (32)"
            self.char_data = new_ctls
            self.char_data.append(-2)
            while len(self.char_data) < jmbConst.JIMAKU_CHAR_MAX:
                self.char_data.append(-1)
        else:
            assert len(new_ctls) == jmbConst.JIMAKU_CHAR_MAX, "length of control codes should be the same as the maximum length (32)"
            self.char_data = new_ctls
        for i in range(jmbConst.JIMAKU_RUBI_DAT_MAX):
            self.rubi_data[i].clear()

    @checkSize
    def read(self, fp):
        handler = EndianHandler(self.__big_endian)
        self.wait = handler.unpack('i', fp.read(4))[0]          # s32
        self.disp_time = handler.unpack('i', fp.read(4))[0]     # s32
        # 读取字符数据
        self.char_data = list(handler.unpack_array(
            'h', jmbConst.JIMAKU_CHAR_MAX, fp.read(2 * jmbConst.JIMAKU_CHAR_MAX)
        ))
        # 读取注音数据
        self.rubi_data = []
        for _ in range(jmbConst.JIMAKU_RUBI_DAT_MAX):
            self.rubi_data.append(stRubiDat(fp, self.__big_endian))

    @checkSize
    def write(self, fp):
        handler = EndianHandler(self.__big_endian)
        fp.write(handler.pack('i', self.wait))             # s32
        fp.write(handler.pack('i', self.disp_time))        # s32

        fp.write(handler.pack_array('h', self.char_data))

        for rubi in self.rubi_data:
            rubi.write(fp)

    def __repr__(self):
        char_str = ''.join([chr(c) if c > 0 else f'[{c}]' for c in self.char_data[:8]])
        return (f"stJimaku(wait={self.wait}, disp_time={self.disp_time}, "
                f"char_data='{char_str}...', rubi_data={len(self.rubi_data)} items)")

class stOneSentence:
    def __init__(self, fp = None, bigEndian = False):
        self.STRUCT_SIZE = 6860
        self.info : stInfo = stInfo()                  # stInfo对象 (76)
        self.jimaku_list : list[stJimaku_JA] = []      # stJimaku对象列表（jmbConst.JIMAKU_LINE_MAX个） (16 * 424)
        self.__big_endian = bigEndian
        if fp is not None:
            self.read(fp)

    def valid_jmk_num(self) -> int:
        assert len(self.jimaku_list) > 0, "jimaku_list should not be empty"
        ret = 0
        for jmk in self.jimaku_list:
            if not jmk.valid():
                return ret
            ret += 1
        return ret

    @checkSize
    def read(self, fp):
        # 读取stInfo
        self.info.read(fp)
        # 读取stJimaku列表
        self.jimaku_list = []
        for _ in range(jmbConst.JIMAKU_LINE_MAX):
            jimaku = stJimaku_JA(fp, self.__big_endian)
            self.jimaku_list.append(jimaku)
        assert len(self.jimaku_list) == jmbConst.JIMAKU_LINE_MAX, "stJimaku list size error"

    @checkSize
    def write(self, fp):
        self.info.write(fp)
        for jimaku in self.jimaku_list:
            jimaku.write(fp)

    def __repr__(self):
        return (f"stOneSentence(\n  info={self.info},\n  "
                f"jimaku_list=[{len(self.jimaku_list)} items])")

class stFontParam:
    def __init__(self, fp=None, bigEndian=False, *, u=0, v=0, w=0, h=0):
        self.u: int = u             # u16
        self.v: int = v             # u16
        self.w: int = w             # u16
        self.h: int = h             # u16
        self.__big_endian = bigEndian
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        endian = '>' if self.__big_endian else '<'
        self.u, self.v, self.w, self.h = struct.unpack(f'{endian}4H', fp.read(8))

    def write(self, fp):
        endian = '>' if self.__big_endian else '<'
        fp.write(struct.pack(f'{endian}4H', self.u, self.v, self.w, self.h))

    def __repr__(self):
        return (f"stFontParam(u={self.u}, v={self.v}, w={self.w}, h={self.h})")

    def __eq__(self, other):
        if not isinstance(other, stFontParam):
            return False
        return (
            self.u == other.u and
            self.v == other.v and
            self.w == other.w and
            self.h == other.h
        )

class texStrImageHeader:
    def __init__(self, fp=None):
        self.STRUCT_SIZE = 32
        self.magic = b'\x00'*8
        self.magic_padding = b'\x00'*4
        self.height = 0                 # int
        self.strPackNum = 0             # int, 文字列pack的数量
        self.strNum = 0                 # int, 文字列的数量
        self.chrNum = 0                 # int, 文字数
        self.tume = 0                   # int, 文字间距
        if fp is not None:
            self.read(fp)

    @checkSize
    def read(self, fp):
        self.magic = fp.read(8)
        assert self.magic == b"STRIMAGE"

        self.magic_padding = fp.read(4)
        assert self.magic_padding == b"\x00"*4

        self.height     = struct.unpack('<i', fp.read(4))[0]
        self.strPackNum = struct.unpack('<i', fp.read(4))[0]
        self.strNum     = struct.unpack('<i', fp.read(4))[0]
        self.chrNum     = struct.unpack('<i', fp.read(4))[0]
        self.tume       = struct.unpack('<i', fp.read(4))[0]

    @checkSize
    def write(self, fp):
        fp.write(self.magic)
        fp.write(self.magic_padding)
        fp.write(struct.pack('<i', self.height))
        fp.write(struct.pack('<i', self.strPackNum))
        fp.write(struct.pack('<i', self.strNum))
        fp.write(struct.pack('<i', self.chrNum))
        fp.write(struct.pack('<i', self.tume))

    def __repr__(self):
        return (
            f"texStrImageHeader(\n"
            f"  magic={self.magic!r},\n"
            f"  magic_padding={self.magic_padding!r},\n"
            f"  height={self.height},\n"
            f"  strPackNum={self.strPackNum},\n"
            f"  strNum={self.strNum},\n"
            f"  chrNum={self.chrNum},\n"
            f"  tume={self.tume}\n"
            f")"
        )

class SIStrPack:
    def __init__(self, fp=None):
        self.STRUCT_SIZE = 62
        self.strIndex:list[int] = []
        if fp is not None:
            self.read(fp)

    @checkSize
    def read(self, fp):
        self.strIndex = []
        for _ in range(jmbConst.STRIMAGE_SIMAXSTRNUM):
            index = struct.unpack('<h', fp.read(2))[0]
            self.strIndex.append(index)

    @checkSize
    def write(self, fp):
        assert len(self.strIndex) == jmbConst.STRIMAGE_SIMAXSTRNUM
        for index in self.strIndex:
            fp.write(struct.pack('<h', index))

    def __repr__(self):
        return f"SIStrPack(strIndex[{len(self.strIndex)}]={self.strIndex})"

class SIStr:
    def __init__(self, fp=None):
        self.STRUCT_SIZE = 258
        self.strIndex:list[int] = []
        if fp is not None:
            self.read(fp)

    @checkSize
    def read(self, fp):
        self.strIndex = []
        for _ in range(jmbConst.STRIMAGE_SIMAXSTRCHRNUM):
            chr = struct.unpack('<h', fp.read(2))[0]
            self.strIndex.append(chr)

    @checkSize
    def write(self, fp):
        assert len(self.strIndex) == jmbConst.STRIMAGE_SIMAXSTRCHRNUM
        for chr in self.strIndex:
            fp.write(struct.pack('<h', chr))

    def __repr__(self):
        return f"SIStr(strIndex[{len(self.strIndex)}]={self.strIndex})"

class SIChr:
    def __init__(self, fp=None):
        self.STRUCT_SIZE = 24
        self.code   = 0         # I
        self.x      = 0         # H
        self.y      = 0         # H
        self.w      = 0         # H
        self.h      = 0         # H
        self.dx     = 0         # h
        self.dy     = 0         # h
        self.addx   = 0         # H
        self.addw   = b'\x00'   # char
        self.code2  = 0         # I
        if fp is not None:
            self.read(fp)

    @checkSize
    def read(self, fp):
        self.code   = struct.unpack('<I', fp.read(4))[0]
        self.x      = struct.unpack('<H', fp.read(2))[0]
        self.y      = struct.unpack('<H', fp.read(2))[0]
        self.w      = struct.unpack('<H', fp.read(2))[0]
        self.h      = struct.unpack('<H', fp.read(2))[0]
        self.dx     = struct.unpack('<h', fp.read(2))[0]
        self.dy     = struct.unpack('<h', fp.read(2))[0]
        self.addx   = struct.unpack('<H', fp.read(2))[0]
        self.addw   = fp.read(1)
        _ = fp.read(1)
        self.code2  = struct.unpack('<I', fp.read(4))[0]

    @checkSize
    def write(self, fp):
        fp.write(struct.pack('<I', self.code))
        fp.write(struct.pack('<H', self.x))
        fp.write(struct.pack('<H', self.y))
        fp.write(struct.pack('<H', self.w))
        fp.write(struct.pack('<H', self.h))
        fp.write(struct.pack('<h', self.dx))
        fp.write(struct.pack('<h', self.dy))
        fp.write(struct.pack('<H', self.addx))
        fp.write(self.addw)
        fp.write(b'\x00')  # padding
        fp.write(struct.pack('<I', self.code2))

    def __repr__(self):
        return (f"SIChr(code={chr(self.code)!r} (0x{self.code:04X}), x={self.x}, y={self.y}, "
                f"w={self.w}, h={self.h}, dx={self.dx}, dy={self.dy}, addx={self.addx}, "
                f"addw={self.addw}, code2={chr(self.code2)!r} (0x{self.code2:04X}))")


class texStrImage:
    def __init__(self, fp=None):
        self.header : texStrImageHeader
        self.strpack : list[SIStrPack] = []
        self.str : list[SIStr] = []
        self.chb : list[SIChr] = []
        self.tex : stTex
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        self.header = texStrImageHeader(fp)

        self.strpack = []
        for i in range(self.header.strPackNum):
            self.strpack.append(SIStrPack(fp))

        self.str = []
        for i in range(self.header.strNum):
            self.str.append(SIStr(fp))

        self.chb = []
        for i in range(self.header.chrNum):
            self.chb.append(SIChr(fp))

        self.tex = stTex(fp)

    def write(self, fp):
        assert self.header.strPackNum == len(self.strpack)
        assert self.header.strNum == len(self.str)
        assert self.header.chrNum == len(self.chb)
        self.header.write(fp)
        for i in range(self.header.strPackNum):
            self.strpack[i].write(fp)
        for i in range(self.header.strNum):
            self.str[i].write(fp)
        for i in range(self.header.chrNum):
            self.chb[i].write(fp)
        self.tex.write(fp)

class texMeta:
    def __init__(self, fp=None, bigEndian = False):
        self.STRUCT_SIZE = 72
        self.magic = b'\x00'*4
        self.encoding = b'\x00'*4   # 4 bytes, 0,1,2,... = I4/I8/IA4/IA8/RGB565/RGB5A3/RGBA8(32?)/...
        self.w = 0                  # u16, 2 bytes
        self.h = 0                  # u16, 2 bytes
        self.dds_size = 0           # u32, 4 bytes
        self.__big_endian = bigEndian
        if fp is not None:
            self.read(fp)

    @checkSize
    def read(self, fp):
        handler = EndianHandler(self.__big_endian)
        self.magic = fp.read(4)
        assert self.magic == b'GCT0' or self.magic == b'\x00'*4, f"Assertion Failed. read {self.magic}, expect: 'GCT0'/'0000'"

        self.encoding = fp.read(4)

        self.w = handler.unpack('H', fp.read(2))[0]
        self.h = handler.unpack('H', fp.read(2))[0]
        assert fp.read(4)   == b'\x00'*4
        assert fp.read(4)   == (b'\x00\x00\x00@' if self.__big_endian else b'@\x00\x00\x00'), f"Assertion Failed. read {fp.read(4)}, expect: '@'/'0000'"
        assert fp.read(44)  == b'\x00' * 44
        assert fp.read(4)   == (b'XT7K' if self.__big_endian else b'K7TX')
        self.dds_size = handler.unpack('I', fp.read(4))[0]

    @checkSize
    def write(self, fp):
        handler = EndianHandler(self.__big_endian)
        fp.write(self.magic)
        fp.write(self.encoding)
        fp.write(handler.pack('H', self.w))
        fp.write(handler.pack('H', self.h))
        fp.write(b'\x00'*4)
        fp.write(b'\x00\x00\x00@' if self.__big_endian else b'@\x00\x00\x00')
        fp.write(b'\x00'*44)
        fp.write(b'XT7K' if self.__big_endian else b'K7TX')
        fp.write(handler.pack('I', self.dds_size))

    def __repr__(self):
        return (f"texMeta(magic={self.magic}, encoding={self.encoding}, w={self.w}, h={self.h}, dds_size={self.dds_size})")

class stTex:
    def __init__(self, fp=None, bigEndian = False):
        self.header : texMeta
        self.dds : bytes
        self.__big_endian = bigEndian
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        self.header = texMeta(fp, self.__big_endian)
        self.dds = fp.read(self.header.dds_size)
        assert self.dds[:4] == b'DDS ', f"Readed magic number:{self.dds[:4]}, expect: 'DDS '; Please check if it is a DDS texture."

    def write(self, fp):
        self.header.write(fp)
        fp.write(self.dds)

    def dump(self, filename):
        with open(filename, 'wb') as wfp:
            wfp.write(self.dds)

    @classmethod
    def load(cls, fp):
        return cls(fp)

    def __repr__(self):
        return (f"stTex : header = {self.header}, len(dds) = {len(self.dds)}")

class oldGCTex:
    def __init__(self, fp=None, bigEndian = False):
        self.header_magic = b'\x00'*4
        self.header_encoding = b'\x00'*4
        self.header_w = 0                   # u16, 2 bytes
        self.header_h = 0                   # u16, 2 bytes
        self.flags = b'\x00'*4
        self.content_offset = 0             # u32, 4 bytes
        self.texture : bytes
        self.__big_endian = bigEndian
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        handler = EndianHandler(self.__big_endian)
        self.header_magic = fp.read(4)
        self.header_encoding = fp.read(4)
        self.header_w = handler.unpack('H', fp.read(2))[0]
        self.header_h = handler.unpack('H', fp.read(2))[0]
        self.flags = fp.read(4)
        self.content_offset = handler.unpack('I', fp.read(4))[0]
        fp.seek(fp.tell() + self.content_offset - 20)
        self.texture = fp.read()

    def write(self, fp):
        handler = EndianHandler(self.__big_endian)
        fp.write(self.header_magic)
        fp.write(self.header_encoding)
        fp.write(handler.pack('H', self.header_w))
        fp.write(handler.pack('H', self.header_h))
        fp.write(self.flags)
        fp.write(handler.pack('I', self.content_offset))
        fp.write(b'\x00' * (self.content_offset - 20))
        fp.write(self.texture)

    def __repr__(self):
        return (f"oldGCTex(header_magic={self.header_magic}, header_encoding={self.header_encoding}, header_w={self.header_w}, header_h={self.header_h}, flags={self.flags}, content_offset={self.content_offset}, len(texture)={len(self.texture)})")


stJimaku = Union[stJimaku_JA, stJimaku_US]
MetaData = Union[MetaData_JA, MetaData_US]