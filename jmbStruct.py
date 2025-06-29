from typing import Union
import jmbConst
import jmbUtils
from dataclasses import dataclass

import struct
import os

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

class MetaData_US:
    def __init__(self, fp = None):
        self.sentence_num : int = 0                 # s16
        self.char_num : int = 0                     # s16
        self.sentence_offset : int = 0              # u32
        self.char_offset : int = 0                  # u32
        self.tex_offset : int = 0                   # u32

        if fp is not None:
            self.read(fp)

    def read(self, fp):
        self.sentence_num = struct.unpack('<h', fp.read(2))[0]      # s16
        self.char_num = struct.unpack('<h', fp.read(2))[0]          # s16
        self.sentence_offset = struct.unpack('<I', fp.read(4))[0]   # u32
        self.char_offset = struct.unpack('<I', fp.read(4))[0]       # u32
        self.tex_offset = struct.unpack('<I', fp.read(4))[0]        # u32

    def write(self, fp):
        fp.write(struct.pack('<h', self.sentence_num))
        fp.write(struct.pack('<h', self.char_num))
        fp.write(struct.pack('<I', self.sentence_offset))
        fp.write(struct.pack('<I', self.char_offset))
        fp.write(struct.pack('<I', self.tex_offset))

    def dump(self, filename):
        NotImplemented

    @classmethod
    def load(cls, filename):
        meta = cls()
        NotImplemented

    def __repr__(self):
        return (
            f"MetaData_US(jimaku_num={self.sentence_num}, "
            f"char_num={self.char_num}, "
            f"jimaku_offset={self.sentence_offset}, "
            f"char_offset={self.char_offset}, "
            f"tex_offset={self.tex_offset}, "
        )

class MetaData_JA:
    def __init__(self, fp = None):
        self.sentence_num : int = 0                 # s16
        self.char_num : int = 0                     # s16
        self.sentence_offset : int = 0              # u32
        self.char_offset : int = 0                  # u32
        self.tex_offset : int = 0                   # u32
        self.s_motion_offset : int = 0              # u32
        self.s_motion_size_tbl : list[int] = []     # u32[] NOTE: 不考虑tbl，大小至少为20
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        self.sentence_num = struct.unpack('<h', fp.read(2))[0]      # s16
        self.char_num = struct.unpack('<h', fp.read(2))[0]          # s16
        self.sentence_offset = struct.unpack('<I', fp.read(4))[0]   # u32
        self.char_offset = struct.unpack('<I', fp.read(4))[0]       # u32
        self.tex_offset = struct.unpack('<I', fp.read(4))[0]        # u32
        self.s_motion_offset = struct.unpack('<I', fp.read(4))[0]   # u32
        self.s_motion_size_tbl = list(struct.unpack(                # u32[]
            f'<{self.sentence_num}I',
            fp.read(4 * self.sentence_num)
        ))

    def write(self, fp):
        fp.write(struct.pack('<h', self.sentence_num))
        fp.write(struct.pack('<h', self.char_num))
        fp.write(struct.pack('<I', self.sentence_offset))
        fp.write(struct.pack('<I', self.char_offset))
        fp.write(struct.pack('<I', self.tex_offset))
        fp.write(struct.pack('<I', self.s_motion_offset))
        fp.write(struct.pack(f'<{self.sentence_num}I', *self.s_motion_size_tbl))

    def dump(self, filename):
        with open(filename, 'wb') as f:
            self.write(f)

    @classmethod
    def load(cls, filename):
        meta = cls()
        NotImplemented

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
    def __init__(self, fp = None):
        self.STRUCT_SIZE = 76
        self.wait = 0            # s32
        self.hps_file = ''       # （FILE_LENGTH bytes）
        self.mth_file = ''       # （FILE_LENGTH bytes）
        self.back_locate = 0     # s16
        self.countinue = 0       # s16
        self.key = 0             # s16
        self.padding = b''
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        before = fp.tell()
        self.wait = struct.unpack('<i', fp.read(4))[0]         # s32
        self.hps_file = read_c_string(fp.read(jmbConst.FILE_LENGTH))
        self.mth_file = read_c_string(fp.read(jmbConst.FILE_LENGTH))
        self.back_locate = struct.unpack('<h', fp.read(2))[0]  # s16
        self.countinue = struct.unpack('<h', fp.read(2))[0]    # s16
        self.key = struct.unpack('<h', fp.read(2))[0]          # s16
        self.padding = fp.read(2) # NOTE: 4-byte alignment padding for struct
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def write(self, fp):
        before = fp.tell()
        fp.write(struct.pack('<i', self.wait))             # s32
        fp.write(write_c_string(self.hps_file, jmbConst.FILE_LENGTH))
        fp.write(write_c_string(self.mth_file, jmbConst.FILE_LENGTH))
        fp.write(struct.pack('<h', self.back_locate))      # s16
        fp.write(struct.pack('<h', self.countinue))        # s16
        fp.write(struct.pack('<h', self.key))              # s16
        fp.write(self.padding) # NOTE: alignment padding for struct
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)
        # print("\t\t !stInfo <-", after)

    def dump(self, filename):
        with open(filename, 'wb') as f:
            self.write(f)

    @classmethod
    def load(cls, fp):
        NotImplemented

    def __repr__(self):
        return (f"stInfo(wait={self.wait}, hps_file='{self.hps_file}', "
                f"mth_file='{self.mth_file}', "
                f"back_locate={self.back_locate}, countinue={self.countinue}, key={self.key}, padding={self.padding})")

class stRubiDat:
    def __init__(self, fp=None):
        self.STRUCT_SIZE = 22
        self.from_num : int = -1                # s8
        self.to_num : int = -1                  # s8
        self.char_id : list[int] = []           # s16[jmbConst.JIMAKU_RUBI_MAX]
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        before = fp.tell()
        self.from_num = struct.unpack('<b', fp.read(1))[0]       # s8
        self.to_num = struct.unpack('<b', fp.read(1))[0]         # s8
        self.char_id = list(struct.unpack(
            f'<{jmbConst.JIMAKU_RUBI_MAX}h',
            fp.read(2 * jmbConst.JIMAKU_RUBI_MAX)
        ))
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def write(self, fp):
        before = fp.tell()
        fp.write(struct.pack('<b', self.from_num))   # s8
        fp.write(struct.pack('<b', self.to_num))     # s8
        fp.write(struct.pack(
            f'<{jmbConst.JIMAKU_RUBI_MAX}h',
            *self.char_id
        ))
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def dump(self, fp):
        NotImplemented

    def clear(self):
        self.from_num = -1
        self.to_num = -1
        self.char_id = [-1] * jmbConst.JIMAKU_RUBI_MAX

    @classmethod
    def load(cls, fp):
        return cls(fp)

    def __repr__(self):
        if self.from_num != -1 and self.to_num != -1:
            valid_rubis = [num for num in self.char_id if num != -1]
            return f"fstRubiDat({self.from_num}->{self.to_num}, {valid_rubis})"
        else:
            return f""

class stJimaku_US:
    def __init__(self, fp = None):
        self.STRUCT_SIZE = 264
        self.wait = 0                               # s32
        self.disp_time = 0                          # s32
        self.char_data : list[int]  = []            # s16[jmbConst.US_JIMAKU_CHAR_MAX] (2 * 128 = 256)

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
        assert(len(new_ctls) > 0)
        needs_padding : bool = not (-2 in new_ctls)
        if needs_padding:
            assert(len(new_ctls) < jmbConst.US_JIMAKU_CHAR_MAX)
            self.char_data = new_ctls
            self.char_data.append(-2)
            while len(self.char_data) < jmbConst.US_JIMAKU_CHAR_MAX:
                self.char_data.append(-1)
        else:
            assert(len(new_ctls) == jmbConst.US_JIMAKU_CHAR_MAX)
            self.char_data = new_ctls

    def read(self, fp):
        before = fp.tell()
        self.wait = struct.unpack('<i', fp.read(4))[0]          # s32
        self.disp_time = struct.unpack('<i', fp.read(4))[0]     # s32
        # 读取字符数据
        self.char_data = list(struct.unpack(
            f'<{jmbConst.US_JIMAKU_CHAR_MAX}h',
            fp.read(2 * jmbConst.US_JIMAKU_CHAR_MAX)
        ))
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def write(self, fp):
        before = fp.tell()
        fp.write(struct.pack('<i', self.wait))             # s32
        fp.write(struct.pack('<i', self.disp_time))        # s32

        fp.write(struct.pack(
            f'<{jmbConst.US_JIMAKU_CHAR_MAX}h',
            *self.char_data
        ))
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)
        # print("\t\t !stJimaku <-", after)

    def dump(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as fp:
            # 写入wait
            fp.write(f"wait = {self.wait}\n")
            # 写入disp_time
            fp.write(f"disp_time = {self.disp_time}\n")
            # 写入char_data
            char_str = " ".join(str(c) for c in jmbUtils.display_char_data(self.char_data))
            fp.write(f"{char_str}\n")

    @classmethod
    def load(cls, filename):
        jimaku = cls()
        with open(filename, 'r') as fp:
            lines = fp.readlines()
            assert(len(lines) == 3)

            # 解析wait
            wait_line = lines[0].strip()
            if not wait_line.startswith("wait = "):
                raise ValueError("Invalid wait line format")
            jimaku.wait = int(wait_line[7:])

            # 解析disp_time
            disp_line = lines[1].strip()
            if not disp_line.startswith("disp_time = "):
                raise ValueError("Invalid disp_time line format")
            jimaku.disp_time = int(disp_line[12:])

            # 解析char_data
            char_line = lines[2].strip()
            char_ctls = [int(c) for c in char_line.split()]
            assert(len(char_ctls) == jmbConst.US_JIMAKU_CHAR_MAX)
            jimaku.overwrite_ctl(char_ctls)

    def __repr__(self):
        char_str = ''.join([chr(c) if c > 0 else f'[{c}]' for c in self.char_data[:8]])
        return (f"stJimaku_US(wait={self.wait}, disp_time={self.disp_time}, "
                f"char_data='{char_str}...')")

class stJimaku_JA:
    def __init__(self, fp = None):
        self.STRUCT_SIZE = 424
        self.wait = 0             # s32
        self.disp_time = 0        # s32
        self.char_data : list[int]  = []            # s16[jmbConst.JIMAKU_CHAR_MAX] (2 * 32 = 64)
        self.rubi_data : list[stRubiDat] = []       # stRubiDat[jmbConst.JIMAKU_RUBI_DAT_MAX] (22 * 16 = 352)
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
        assert(len(new_ctls) > 0)
        needs_padding : bool = not (-2 in new_ctls)
        if needs_padding:
            assert(len(new_ctls) < jmbConst.JIMAKU_CHAR_MAX)
            self.char_data = new_ctls
            self.char_data.append(-2)
            while len(self.char_data) < jmbConst.JIMAKU_CHAR_MAX:
                self.char_data.append(-1)
        else:
            assert(len(new_ctls) == jmbConst.JIMAKU_CHAR_MAX)
            self.char_data = new_ctls
        for i in range(jmbConst.JIMAKU_RUBI_DAT_MAX):
            self.rubi_data[i].clear()

    def read(self, fp):
        before = fp.tell()
        self.wait = struct.unpack('<i', fp.read(4))[0]          # s32
        self.disp_time = struct.unpack('<i', fp.read(4))[0]     # s32
        # 读取字符数据
        self.char_data = list(struct.unpack(
            f'<{jmbConst.JIMAKU_CHAR_MAX}h',
            fp.read(2 * jmbConst.JIMAKU_CHAR_MAX)
        ))
        # 读取注音数据
        self.rubi_data = []
        for _ in range(jmbConst.JIMAKU_RUBI_DAT_MAX):
            self.rubi_data.append(stRubiDat(fp))
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def write(self, fp):
        before = fp.tell()
        fp.write(struct.pack('<i', self.wait))             # s32
        fp.write(struct.pack('<i', self.disp_time))        # s32

        fp.write(struct.pack(
            f'<{jmbConst.JIMAKU_CHAR_MAX}h',
            *self.char_data
        ))

        for rubi in self.rubi_data:
            rubi.write(fp)

        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)
        # print("\t\t !stJimaku <-", after)

    def dump(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as fp:
            # 写入wait
            fp.write(f"wait = {self.wait}\n")
            # 写入disp_time
            fp.write(f"disp_time = {self.disp_time}\n")
            # 写入char_data
            char_str = " ".join(str(c) for c in jmbUtils.display_char_data(self.char_data))
            fp.write(f"{char_str}\n")

    @classmethod
    def load(cls, filename):
        jimaku = cls()
        with open(filename, 'r') as fp:
            lines = fp.readlines()
            assert(len(lines) == 3)

            # 解析wait
            wait_line = lines[0].strip()
            if not wait_line.startswith("wait = "):
                raise ValueError("Invalid wait line format")
            jimaku.wait = int(wait_line[7:])

            # 解析disp_time
            disp_line = lines[1].strip()
            if not disp_line.startswith("disp_time = "):
                raise ValueError("Invalid disp_time line format")
            jimaku.disp_time = int(disp_line[12:])

            # 解析char_data
            char_line = lines[2].strip()
            char_ctls = [int(c) for c in char_line.split()]
            assert(len(char_ctls) == jmbConst.JIMAKU_CHAR_MAX)
            jimaku.overwrite_ctl(char_ctls)

            # 填充空rubi
            rubis = []
            for _ in range(jmbConst.JIMAKU_RUBI_DAT_MAX):
                rubi = stRubiDat()
                rubi.clear()
                rubis.append(rubi)
            jimaku.rubi_data = rubis

    def __repr__(self):
        char_str = ''.join([chr(c) if c > 0 else f'[{c}]' for c in self.char_data[:8]])
        return (f"stJimaku(wait={self.wait}, disp_time={self.disp_time}, "
                f"char_data='{char_str}...', rubi_data={len(self.rubi_data)} items)")

class stOneSentence:
    def __init__(self, fp = None):
        self.STRUCT_SIZE = 6860
        self.info : stInfo = stInfo()               # stInfo对象 (76)
        self.jimaku_list : list[stJimaku_JA] = []      # stJimaku对象列表（jmbConst.JIMAKU_LINE_MAX个） (16 * 424)
        if fp is not None:
            self.read(fp)

    def valid_jmk_num(self) -> int:
        assert(len(self.jimaku_list) > 0)
        ret = 0
        for jmk in self.jimaku_list:
            if not jmk.valid():
                return ret
            ret += 1

    def read(self, fp):
        before = fp.tell()
        # 读取stInfo
        self.info.read(fp)

        # 读取stJimaku列表
        self.jimaku_list = []
        for _ in range(jmbConst.JIMAKU_LINE_MAX):
            jimaku = stJimaku_JA(fp)
            self.jimaku_list.append(jimaku)
        assert(len(self.jimaku_list) == jmbConst.JIMAKU_LINE_MAX)
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def write(self, fp):
        before = fp.tell()
        self.info.write(fp)
        for jimaku in self.jimaku_list:
            jimaku.write(fp)
        after = fp.tell()
        # print("\t !stOneSentence <-", after)

        assert(after - before == self.STRUCT_SIZE)

    def dump(self, filename):
        NotImplemented

    @classmethod
    def load(cls, fp):
        sentence = cls()
        NotImplemented

    def __repr__(self):
        return (f"stOneSentence(\n  info={self.info},\n  "
                f"jimaku_list=[{len(self.jimaku_list)} items])")

class stFontParam:
    def __init__(self, fp=None, *, u=0, v=0, w=0, h=0):
        self.u: int = u             # u16
        self.v: int = v             # u16
        self.w: int = w             # u16
        self.h: int = h             # u16
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        self.u, self.v, self.w, self.h = struct.unpack('<4H', fp.read(8))

    def write(self, fp):
        fp.write(struct.pack('<4H', self.u, self.v, self.w, self.h))

    def dump(self, fp):
        NotImplemented

    @classmethod
    def load(cls, fp):
        return cls(fp)

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

class texMeta:
    def __init__(self, fp=None):
        self.STRUCT_SIZE = 72
        self.w = 0              # u16, 2 bytes
        self.h = 0              # u16, 2 bytes
        self.dds_size = 0       # u32, 4 bytes
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        before = fp.tell()
        assert(fp.read(4) == b'\x00'*4)
        assert(fp.read(4) == b'\x06\x00\x00\x00')
        self.w = struct.unpack('<H', fp.read(2))[0]
        self.h = struct.unpack('<H', fp.read(2))[0]
        assert(fp.read(4) == b'\x00'*4)
        assert(fp.read(4) == b'@\x00\x00\x00')
        assert(fp.read(44) == b'\x00' * 44)
        assert(fp.read(4) == b'K7TX')
        self.dds_size = struct.unpack('<I', fp.read(4))[0]
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def write(self, fp):
        before = fp.tell()
        fp.write(b'\x00'*4)
        fp.write(b'\x06\x00\x00\x00')
        fp.write(struct.pack('<H', self.w))
        fp.write(struct.pack('<H', self.h))
        fp.write(b'\x00'*4)
        fp.write(b'@\x00\x00\x00')
        fp.write(b'\x00'*44)
        fp.write(b'K7TX')
        fp.write(struct.pack('<I', self.dds_size))
        after = fp.tell()
        assert(after - before == self.STRUCT_SIZE)

    def dump(self, filename):
        NotImplemented

    def load(self, filename):
        NotImplemented

    def __repr__(self):
        return (f"texMeta(w={self.w}, h={self.h}, dds_size={self.dds_size})")

class stTex:
    def __init__(self, fp=None):
        self.header : texMeta
        self.dds : bytes
        if fp is not None:
            self.read(fp)

    def read(self, fp):
        self.header = texMeta(fp)
        self.dds = fp.read(self.header.dds_size)
        assert(self.dds[:4] == b'DDS ')

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
        # TODO: 更新repr
        return (f"stTex : len(header) = {len(self.header)}, len(dds) = {len(self.dds)}")


stJimaku = Union[stJimaku_JA, stJimaku_US]
MetaData = Union[MetaData_JA, MetaData_US]