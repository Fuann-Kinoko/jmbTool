from typing import TypeGuard
from jmbTool.jmbData import *

def _TYPE_is_JA(obj: gDat) -> TypeGuard[gDat_JA]:
    return isinstance(obj, gDat_JA)
def _TYPE_is_US(obj: gDat) -> TypeGuard[gDat_US]:
    return isinstance(obj, gDat_US)
