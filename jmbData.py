from jmbStruct import *
from jmbNumeric import S16
import jmbConst
import jmbUtils

from enum import Enum, auto
from copy import copy
from abc import ABC, abstractmethod
import io

import wand.image

class JmkKind(Enum):
    JA = auto()
    US = auto()

class BaseGdat(ABC):
    def __init__(self, source = None):
        self.fParams : list[stFontParam]
        self.tex : stTex

        if source is not None:
            if isinstance(source, str):
                with open(source, 'rb') as fp:
                    self.read(fp)
            else:
                self.read(source)

    @classmethod
    def create(cls, source, kind:JmkKind):
        """
        source: filepath (str) | fp
        kind: JmkKind (JA | US)
        """
        assert(isinstance(kind, JmkKind))
        if kind == JmkKind.JA:
            return gDat_JA(source)
        elif kind == JmkKind.US:
            return gDat_US(source)
        else:
            assert False, "unreachable"

    @abstractmethod
    def read(self, fp):
        pass

    @abstractmethod
    def ready_to_write(self) -> bool:
        pass

    def write_to_file(self, writepath: str, validation=True):
        os.makedirs(os.path.dirname(writepath), exist_ok=True)
        with open(writepath, 'wb') as fp:
            self.write(fp, validation)

    @abstractmethod
    def recalculate_meta(self):
        pass

    @abstractmethod
    def write(self, fp, validation=True):
        pass

    def no_diff_with(self, filename: str) -> bool:
        gen_buf = io.BytesIO()
        self.write(gen_buf, validation=False)
        with open(filename, 'rb') as f_ori:
            return f_ori.read() == gen_buf.getvalue()

    def reimport_tex(self, filename: str):
        assert os.path.exists(filename)
        old_len = len(self.tex.dds)
        old_w, old_h = self.tex.header.w, self.tex.header.h

        with open(filename, 'rb') as fp:
            dds_bytes = fp.read()
            self.tex.dds = dds_bytes
            assert self.tex.dds[:4] == b'DDS '

        new_len = len(self.tex.dds)
        print(f"tex reimported from {filename} ({old_len} -> {new_len})")

        import wand.image
        img = wand.image.Image(blob=dds_bytes)
        width, height = img.size
        img.close()
        assert width % 4 == 0 and height % 4 == 0
        self.tex.header.w = width // 4
        self.tex.header.h = height // 4
        self.tex.header.dds_size = new_len
        print(f"DDS Canvas Changed: {old_w}x{old_h} -> {width//4}x{height//4}")

    @abstractmethod
    def update_sentence_ctl(self, translation, char2ctl_lookup: dict[str, int], validation_mode = False):
        pass

class gDat_US(BaseGdat):
    def __init__(self, fp = None):
        self.meta : MetaData_US = None
        self.sentences : list[stJimaku_US] = None
        self.fParams : list[stFontParam] = None
        self.tex : stTex = None

        super().__init__(fp)

    def read(self, fp):
        self.meta = MetaData_US(fp)

        fp.seek(self.meta.sentence_offset)
        self.sentences : list[stJimaku_US] = []
        for _ in range(self.meta.sentence_num):
            self.sentences.append(stJimaku_US(fp))

        fp.seek(self.meta.char_offset)
        self.fParams : list[stFontParam] = []
        for _ in range(self.meta.char_num):
            self.fParams.append(stFontParam(fp))

        fp.seek(self.meta.tex_offset)
        self.tex = stTex(fp)

    def ready_to_write(self) -> bool:
        ready : bool = True
        ready &= (self.meta != None)
        ready &= (self.sentences != None)
        ready &= (self.fParams != None)
        ready &= (self.tex != None)
        return ready

    def recalculate_meta(self):
        assert(self.ready_to_write())
        dummy_fp = io.BytesIO()

        # NOTE: jimaku_offset 前面是Metadata, offset应该不会改变
        self.meta.write(dummy_fp)
        after_meta = dummy_fp.tell()
        assert(after_meta == self.meta.sentence_offset)

        # NOTE: 只要句子个数不变，对char_offset应该不存在修改
        assert(len(self.sentences) == self.meta.sentence_num)
        for sent in self.sentences:
            sent.write(dummy_fp)
        after_sent = dummy_fp.tell()
        if True:
            touch = after_sent
            not_touched : bool = (self.meta.char_offset == touch)
            print(f"修改meta: char_offset {self.meta.char_offset} -> {'[SAME]' if not_touched else touch}")
            self.meta.char_offset = after_sent

        # NOTE: ENABLED: 对fParams的修改
        if True:
            touch = len(self.fParams)
            not_touched : bool = (self.meta.char_num == touch)
            print(f"修改meta: char_num {self.meta.char_num} -> {'[SAME]' if not_touched else touch}")
            self.meta.char_num = len(self.fParams)

        assert(len(self.fParams) == self.meta.char_num)
        for fparam in self.fParams:
            fparam.write(dummy_fp)
        after_char = dummy_fp.tell()
        # padding
        if after_char != self.meta.tex_offset:
            padding_size = 32 - (after_char % 32)
            dummy_fp.write(b'\x00' * padding_size)
            after_char = dummy_fp.tell()
        if True:
            touch = after_char
            not_touched : bool = (self.meta.tex_offset == touch)
            print(f"修改meta: tex_offset {self.meta.tex_offset} -> {'[SAME]' if not_touched else touch}")
            self.meta.tex_offset = after_char

        assert(dummy_fp.tell() == self.meta.tex_offset)
        self.tex.write(dummy_fp)
        del dummy_fp

    def write(self, fp, validation = True):
        assert(self.ready_to_write())
        if validation:
            self.recalculate_meta()
            print("MetaData Recalculated...")

        self.meta.write(fp)
        after_meta = fp.tell()
        # print("!meta <-", after_meta)
        # print("!meta", self.meta.sentence_offset)
        assert after_meta == self.meta.sentence_offset, (
            f"expecting sentence_offset : {self.meta.sentence_offset}",
            f"writed pos after meta : {after_meta}"
        )

        for sent in self.sentences:
            sent.write(fp)

        after_sent = fp.tell()
        # print("!sent <-", after_sent)
        # print("!sent", self.meta.char_offset)
        assert( after_sent == self.meta.char_offset)

        for fparam in self.fParams:
            fparam.write(fp)

        after_char = fp.tell()
        if after_char != self.meta.tex_offset:
            # 补全 0，直到与32 byte alignment
            padding_size = 32 - (after_char % 32)
            fp.write(b'\x00' * padding_size)
        assert(fp.tell() == self.meta.tex_offset)

        self.tex.write(fp)

    def update_sentence_ctl(self, translation: list[str], char2ctl_lookup: dict[str, int], validation_mode = False):
        assert(self.meta.sentence_num == len(translation))
        for i, local_sent in enumerate(translation):
            local_ctls = [char2ctl_lookup[ch] for ch in local_sent]
            assert(len(local_ctls) < jmbConst.US_JIMAKU_CHAR_MAX)
            local_ctls.append(-2)
            while len(local_ctls) < jmbConst.US_JIMAKU_CHAR_MAX:
                local_ctls.append(-1)
            assert(len(local_ctls) == len(self.sentences[i].char_data))

            if validation_mode:
                assert(self.sentences[i].valid_len() == len(local_sent))
                for j, ctl in enumerate(self.sentences[i].char_data):
                    assert(ctl == local_ctls[j])
                print("jmk correct", local_sent)
            else:
                self.sentences[i].overwrite_ctl(local_ctls)

    def flush_fparams(self):
        NotImplemented
        assert len(self.fParams) > 0

class gDat_JA(BaseGdat):
    def __init__(self, fp = None):
        self.meta : MetaData_JA = None
        self.sentences : list[stOneSentence] = None
        self.fParams : list[stFontParam] = None
        self.tex : stTex = None
        self.motions : list[bytes] = None

        self.end_by_tex : bool = False
        super().__init__(fp)

    def read(self, fp):
        self.meta = MetaData_JA(fp)

        fp.seek(self.meta.sentence_offset)
        self.sentences : list[stOneSentence] = []
        for _ in range(self.meta.sentence_num):
            self.sentences.append(stOneSentence(fp))

        fp.seek(self.meta.char_offset)
        self.fParams : list[stFontParam] = []
        for _ in range(self.meta.char_num):
            self.fParams.append(stFontParam(fp))

        fp.seek(self.meta.tex_offset)
        self.tex = stTex(fp)
        after_tex = fp.tell()
        if after_tex % 32 != 0:
            padding_size = 32 - (after_tex % 32)
            self.end_by_tex = (self.meta.s_motion_offset == after_tex + padding_size)
        else:
            self.end_by_tex = (self.meta.s_motion_offset == after_tex)

        if not self.end_by_tex:
            fp.seek(self.meta.s_motion_offset)
            assert(len(self.meta.s_motion_size_tbl) == self.meta.sentence_num)
            self.motions = []
            for cur_motion_size in self.meta.s_motion_size_tbl:
                self.motions.append(fp.read(cur_motion_size))

    def ready_to_write(self) -> bool:
        ready : bool = True
        ready &= (self.meta != None)
        ready &= (self.sentences != None)
        ready &= (self.fParams != None)
        ready &= (self.tex != None)
        if self.end_by_tex:
            return ready
        ready &= (self.motions != None)
        return ready

    def recalculate_meta(self):
        assert(self.ready_to_write())
        dummy_fp = io.BytesIO()

        # NOTE: sentence_offset 前面是Metadata, offset应该不会改变
        self.meta.write(dummy_fp)
        after_meta = dummy_fp.tell()
        assert(after_meta == self.meta.sentence_offset)

        # NOTE: 只要句子个数不变，对char_offset应该不存在修改
        assert(len(self.sentences) == self.meta.sentence_num)
        for sent in self.sentences:
            sent.write(dummy_fp)
        after_sent = dummy_fp.tell()
        if True:
            touch = after_sent
            not_touched : bool = (self.meta.char_offset == touch)
            print(f"修改meta: char_offset {self.meta.char_offset} -> {'[SAME]' if not_touched else touch}")
            self.meta.char_offset = after_sent

        # NOTE: ENABLED: 对fParams的修改
        if True:
            touch = len(self.fParams)
            not_touched : bool = (self.meta.char_num == touch)
            print(f"修改meta: char_num {self.meta.char_num} -> {'[SAME]' if not_touched else touch}")
            self.meta.char_num = len(self.fParams)

        assert(len(self.fParams) == self.meta.char_num)
        for fparam in self.fParams:
            fparam.write(dummy_fp)
        after_char = dummy_fp.tell()
        # padding
        if after_char != self.meta.tex_offset:
            padding_size = 32 - (after_char % 32)
            dummy_fp.write(b'\x00' * padding_size)
            after_char = dummy_fp.tell()
        if True:
            touch = after_char
            not_touched : bool = (self.meta.tex_offset == touch)
            print(f"修改meta: tex_offset {self.meta.tex_offset} -> {'[SAME]' if not_touched else touch}")
            self.meta.tex_offset = after_char

        assert(dummy_fp.tell() == self.meta.tex_offset)
        self.tex.write(dummy_fp)

        # NOTE: ENABLED: 对s_motion_offset的修改
        after_tex = dummy_fp.tell()
        if after_tex % 32 != 0:
            padding_size = 32 - (after_tex % 32)
            dummy_fp.write(b'\x00' * padding_size)
            after_tex = dummy_fp.tell()
        if True:
            touch = after_tex
            not_touched : bool = (self.meta.s_motion_offset == touch)
            print(f"修改meta: s_motion_offset {self.meta.s_motion_offset} -> {'[SAME]' if not_touched else touch}")
            self.meta.s_motion_offset = after_tex

        del dummy_fp

    def write(self, fp, validation = True):
        assert(self.ready_to_write())
        if validation:
            self.recalculate_meta()
            print("MetaData Recalculated...")

        self.meta.write(fp)
        after_meta = fp.tell()
        # print("!meta <-", after_meta)
        # print("!meta", self.meta.sentence_offset)
        assert( after_meta == self.meta.sentence_offset)

        for sent in self.sentences:
            sent.write(fp)

        after_sent = fp.tell()
        # print("!sent <-", after_sent)
        # print("!sent", self.meta.char_offset)
        assert( after_sent == self.meta.char_offset)

        for fparam in self.fParams:
            fparam.write(fp)

        after_char = fp.tell()
        if after_char != self.meta.tex_offset:
            # 补全 0，直到与32 byte alignment
            padding_size = 32 - (after_char % 32)
            fp.write(b'\x00' * padding_size)
        assert(fp.tell() == self.meta.tex_offset)

        self.tex.write(fp)
        after_tex = fp.tell()
        if after_tex != self.meta.s_motion_offset:
            padding_size = 32 - (after_tex % 32)
            fp.write(b'\x00' * padding_size)
        assert(fp.tell() == self.meta.s_motion_offset)

        if not self.end_by_tex:
            for motion in self.motions:
                fp.write(motion)

    def update_sentence_ctl(self, translation: list[list[str]], char2ctl_lookup: dict[str, int], validation_mode = False):
        assert(self.meta.sentence_num == len(translation))

        for i, local_sent in enumerate(translation):
            assert(self.sentences[i].valid_jmk_num() == len(local_sent))

            for j, local_jmk in enumerate(local_sent):
                local_ctls = []
                k = 0
                while k < len(local_jmk):
                    cur_char = local_jmk[k]
                    # Check for @ sequences
                    if cur_char == '@':
                        assert k + 2 < len(local_jmk)
                        assert local_jmk[k+1].isalnum() and local_jmk[k+2].isalnum()
                        local_ctls.append(S16(f"ff{local_jmk[k+1]}{local_jmk[k+2]}").to_int())
                        k += 3
                        continue
                    # Normal character processing
                    local_ctls.append(char2ctl_lookup[cur_char])
                    k += 1

                assert len(local_ctls) < jmbConst.JIMAKU_CHAR_MAX
                local_ctls.append(-2)
                while len(local_ctls) < jmbConst.JIMAKU_CHAR_MAX:
                    local_ctls.append(-1)
                assert len(local_ctls) == len(self.sentences[i].jimaku_list[j].char_data)

                if validation_mode:
                    assert(self.sentences[i].jimaku_list[j].valid_len() == len(local_jmk))
                    for k, ctl in enumerate(self.sentences[i].jimaku_list[j].char_data):
                        assert(ctl == local_ctls[k])
                    print("jmk correct", local_jmk)
                else:
                    self.sentences[i].jimaku_list[j].overwrite_ctl(local_ctls)

    def flush_fparams(self):
        assert len(self.fParams) > 0
        cur_u = 0
        for param in self.fParams:
            if cur_u < param.u:
                param.u = cur_u
            elif param.u == 0:
                cur_u = 0
            # u=0 w=10, cur_u = 0
            # u=11, w=10 cur_uu = 11
            cur_u += param.w

gDat = Union[gDat_JA, gDat_US]