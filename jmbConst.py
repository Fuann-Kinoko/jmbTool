from .jmbNumeric import S16_BE

JIMAKU_TEX_WIDTH = 512
FILE_LENGTH = 32

JIMAKU_CHAR_MAX = 32
JIMAKU_RUBI_MAX = 10
JIMAKU_RUBI_DAT_MAX = 16
JIMAKU_LINE_MAX = 16

US_JIMAKU_CHAR_MAX = 128

STRIMAGE_MAXSTRPACKNUM = 500
STRIMAGE_SIMAXSTRNUM = (30 + 1)
STRIMAGE_SIMAXSTRCHRNUM = (128 + 1)

SATSU_FLAG      = S16_BE("8000")
SHI_FLAG        = S16_BE("7000")
SPACE_H_FLAG    = S16_BE("fffd")
SPACE_Z_FLAG    = S16_BE("fffc")

from enum import Enum, auto

class JmkUsage(Enum):
    Default = auto()
    Name = auto()
    Hato = auto()
    Tutorial = auto()
    Voice = auto()

class JmkKind(Enum):
    JA = auto()
    US = auto()
