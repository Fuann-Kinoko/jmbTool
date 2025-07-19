import itertools
from typing import Union, overload
from jmbConst import JmkKind

class FileLister:
    def __init__(self):
        # i hate overdesign, but i just don't want these variables to pop up in completion
        self._CharaGeki_00_Angel_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00010101/00010101/00010101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00010101/00010101/00010101nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020103/00020103/00020103J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020103/00020103/00020103nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020203/00020203/00020203J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020301/00020301/00020301J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020502/00020502/00020502J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020703/00020703/00020703J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020703/00020703/00020703nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020707/00020707/00020707J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020707/00020707/00020707nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020709/00020709/00020709J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020709/00020709/00020709nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020711/00020711/00020711J.jmb",
        ]
        self._CharaGeki_01_Sunset_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01020101/01020101/01020101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01020201/01020201/01020201J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01020203/01020203/01020203J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01030101/01030101/01030101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01040101/01040101/01040101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050101/01050101/01050101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050102/01050102/01050102J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050102/01050102/01050102nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050203/01050203/01050203J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050203/01050203/01050203nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050204/01050204/01050204J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050206/01050206/01050206J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01060101/01060101/01060101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01060101/01060101/01060101nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01070202/01070202/01070202J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01070210/01070210/01070210J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01090101/01090101/01090101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01090101/01090101/01090101nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01100101/01100101/01100101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01500101/01500101/01500101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01500201/01500201/01500201J.jmb",
        ]
        self._CharaGeki_02_Cloudman_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/02010101/02010101/02010101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/02020101/02020101/02020101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/02020102/02020102/02020102J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/02020201/02020201/02020201J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/02020203/02020203/02020203J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/02030101/02030101/02030101J.jmb",
        ]
        self._CharaGeki_03_Encounter_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03020101/03020101/03020101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03020201/03020201/03020201J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03020203/03020203/03020203J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03030101/03030101/03030101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03040103/03040103/03040103J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03050101/03050101/03050101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03050107/03050107/03050107J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03050109/03050109/03050109J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03060101/03060101/03060101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03060101/03060101/03060101nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03060102/03060102/03060102J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/03080402/03080402/03080402J.jmb",
        ]
        self._CharaGeki_04_Alterego_JA = []
        self._CharaGeki_05_Smile_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05020101/05020101/05020101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05020302/05020302/05020302J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05030101/05030101/05030101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05040101/05040101/05040101J.jmb",
            # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05040101/05040101/05040101nm.jmb", FIXME: edo相关？
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05040201/05040201/05040201J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05070101/05070101/05070101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05080102/05080102/05080102J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05080102/05080102/05080102nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05080202/05080202/05080202J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05080202/05080202/05080202nmJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05090101/05090101/05090101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05090702/05090702/05090702J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05090802/05090802/05090802J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05090803/05090803/05090803J.jmb",
        ]
        self._CharaGeki_06_Lion_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05100103/05100103/05100103J.jmb",
            # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05100105/05100105/05100105J.jmb", # FIXME: 只有一句welcome
            # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05120101/05120101/05120101J.jmb", # FIXME: 空的
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/05500101/05500101/05500101J.jmb",
        ]

        self._Zan_00_Angel_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071010/0071010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071020/0071020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071030/0071030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071040/0071040J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071060/0071060J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071080/0071080J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071100/0071100J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071110/0071110J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071120/0071120J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071130/0071130J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071150/0071150J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071160/0071160J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071170/0071170J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071180/0071180J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071190/0071190J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0072010/0072010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0072020/0072020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0072030/0072030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0072040/0072040J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0072041/0072041J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0072042/0072042J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0073010/0073010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0073011/0073011J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0073020/0073020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0073050/0073050J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0073061/0073061J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0073062/0073062J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0073070/0073070J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0074010/0074010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0074030/0074030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0074040/0074040J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0074060/0074060J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0074070/0074070J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0075010/0075010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0075030/0075030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0075050/0075050J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0076010/0076010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0076020/0076020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0078010/0078010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0078011/0078011J.jmb",
        ]
        self._Zan_01_Sunset_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100020/0100020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100030/0100030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100031/0100031J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100032/0100032J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100033/0100033J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100040/0100040J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100050/0100050J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100061/0100061J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100062/0100062J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100070/0100070J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100071/0100071J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100100/0100100J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100130/0100130J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100151/0100151J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100152/0100152J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100160/0100160J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100180/0100180J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100190/0100190J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100200/0100200J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0100250/0100250J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110000/0110000J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110020/0110020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110030/0110030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110040/0110040J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110101/0110101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110102/0110102J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110111/0110111J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110112/0110112J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110121/0110121J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110122/0110122J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110131/0110131J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110132/0110132J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110200/0110200J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110210/0110210J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110220/0110220J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110230/0110230J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110240/0110240J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110300/0110300J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110310/0110310J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0110510/0110510J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0112030/0112030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0112031/0112031J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0116010/0116010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0121000/0121000J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0121020/0121020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0121030/0121030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0121100/0121100J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0121110/0121110J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0121120/0121120J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0121140/0121140J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0121500/0121500J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0121510/0121510J.jmb",
        ]
        self._Zan_02_Cloudman_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201010/0201010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201020/0201020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201021/0201021J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201030/0201030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201040/0201040J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201050/0201050J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201100/0201100J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201200/0201200J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201300/0201300J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201310/0201310J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201320/0201320J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201330/0201330J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201340/0201340J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201350/0201350J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0201360/0201360J.jmb",
        ]
        self._Zan_03_Encounter_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300100/0300100J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300110/0300110J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300120/0300120J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300130/0300130J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300140/0300140J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300150/0300150J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300200/0300200J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300220/0300220J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300230/0300230J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300250/0300250J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300260/0300260J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300300/0300300J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300301/0300301J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300400/0300400J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300410/0300410J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300420/0300420J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0300600/0300600J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350010/0350010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350020/0350020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350030/0350030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350040/0350040J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350050/0350050J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350060/0350060J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350080/0350080J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350090/0350090J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350100/0350100J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350121/0350121J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350122/0350122J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350131/0350131J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350132/0350132J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350140/0350140J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350141/0350141J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350150/0350150J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350160/0350160J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0350200/0350200J.jmb",
        ]
        self._Zan_04_Alterego_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0400900/0400900J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0401010/0401010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0401020/0401020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0401030/0401030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0401060/0401060J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0401070/0401070J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0401080/0401080J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0401510/0401510J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0401520/0401520J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0401530/0401530J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0401540/0401540J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0402010/0402010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0402020/0402020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0404010/0404010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0404030/0404030J.jmb",
        ]
        self._Zan_05_Smile_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0511210/0511210J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0511220/0511220J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0511230/0511230J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0511240/0511240J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0511250/0511250J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0511260/0511260J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0511310/0511310J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0511400/0511400J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0511500/0511500J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0516010/0516010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0521010/0521010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0521020/0521020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555000/0555000J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555010/0555010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555020/0555020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555030/0555030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555040/0555040J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555050/0555050J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555110/0555110J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555120/0555120J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555130/0555130J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555140/0555140J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555210/0555210J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555220/0555220J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555311/0555311J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555312/0555312J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555321/0555321J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555322/0555322J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555331/0555331J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0555332/0555332J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0557000/0557000J.jmb",
        ]
        self._Zan_06_Lion_JA = []
        self._Zan_99_Extra_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901010/0901010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901020/0901020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901030/0901030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901040/0901040J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901050/0901050J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901060/0901060J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901070/0901070J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901080/0901080J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901090/0901090J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901100/0901100J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901110/0901110J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901120/0901120J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901130/0901130J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901140/0901140J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901150/0901150J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901160/0901160J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901170/0901170J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901180/0901180J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901190/0901190J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901200/0901200J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0901210/0901210J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902010/0902010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902020/0902020J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902030/0902030J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902040/0902040J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902050/0902050J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902060/0902060J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902070/0902070J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902080/0902080J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902090/0902090J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902100/0902100J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902110/0902110J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902120/0902120J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902130/0902130J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902140/0902140J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902150/0902150J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902160/0902160J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902170/0902170J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902210/0902210J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0902220/0902220J.jmb",
        ]
        self._Hato_00_Angel_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato007201J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato007301J.jmb",
        ]
        self._Hato_01_Sunset_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato010001J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato010002J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato010003J.jmb",
        ]
        self._Hato_02_Cloudman_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato020105J.jmb",
        ]
        self._Hato_03_Encounter_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato035001J.jmb",
        ]
        self._Hato_04_Alterego_JA = []
        self._Hato_05_Smile_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato055600J.jmb",
        ]
        self._Hato_06_Lion_JA = []

        self._Movie_00_Angel_JA = []
        self._Movie_01_Sunset_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/Movie/01010101/01010101.jmb",
        ]
        self._Movie_02_Cloudman_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/Movie/clemence/clemence.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/cloudman/cloudman.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/drugstore/drugstore.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/gurad/gurad.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/postman/postman.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/tractor/tractor.jmb",
        ]
        self._Movie_03_Encounter_JA = []
        self._Movie_04_Alterego_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/Movie/04010101/04010101.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/04010201/04010201.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/04010203/04010203.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/04040101/04040101.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/04050101/04050101.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/04050202/04050202.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/04050301/04050301.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/04060101/04060101.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/Movie/04060902/04060902.jmb",
        ]
        self._Movie_05_Smile_JA = []
        self._Movie_06_Lion_JA = [
            # "D:/SteamLibrary/steamapps/common/killer7/Movie/05100201/05100201.jmb", # FIXME: 不确定是否需要
            # "D:/SteamLibrary/steamapps/common/killer7/Movie/05100202/05100202.jmb",
            # "D:/SteamLibrary/steamapps/common/killer7/Movie/051002018/051002018.jmb",
            # "D:/SteamLibrary/steamapps/common/killer7/Movie/051002028/051002028.jmb",
        ]

        self._Panel_00_Angel_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P000304J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P000501J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P000603J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P007201J.jmb",
        ]
        self._Panel_01_Sunset_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P010401J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P010402J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P010403J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P010600J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P011305J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P011403J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P011502J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P011602J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P011603J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P011604J.jmb",
        ]
        self._Panel_02_Cloudman_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P020109J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P020202J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P020203J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P020208J.jmb",
        ]
        self._Panel_03_Encounter_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P030205J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P030409J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P030901J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P035005J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P035010J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P035012J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P035014J.jmb",
        ]
        self._Panel_04_Alterego_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P035105J.jmb", # NOTE: 很神奇但确实是这个
        ]
        self._Panel_05_Smile_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P050103J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P055100J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P055101J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P055102J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P055103J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P055501J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P055700J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P055703J.jmb",
        ]
        self._Panel_06_Lion_JA = []

        self._Stage_00_Angel_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage771_M02J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage771_M02NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage772_M02J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage772_M02NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage772_M03J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage773_M02J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage773_M03NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage773_M04J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage773_M05J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage774_M02J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage774_M02NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage775_M02NMJ.jmb",
        ]
        self._Stage_01_Sunset_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage101_M01J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage102_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage103_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage104_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage105_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage106_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage106_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage107_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage112_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage112_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage113_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage113_M01J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage113_M02J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage113_M03J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage118_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage131_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage131_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage132_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage132_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage133_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage133_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage134_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage135_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage136_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage137_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage138_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage147_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage180_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage190_M01J.jmb",
        ]
        self._Stage_02_Cloudman_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage201_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage201_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage201_M01J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage201_M01NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage203_M01J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage205_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage207_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage208_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage209_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage209_M01J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage211_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage212_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage213_M00J.jmb",
        ]
        self._Stage_03_Encounter_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage306_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage307_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage308_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage309_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage310_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage310_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage313_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage315_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage321_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage321_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage323_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage323_M02J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage324_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage324_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage325_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage325_M03J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage326_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage327_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage327_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage328_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage352_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage353_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage354_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage355_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage355_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage356_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage357_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage358_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage359_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage361_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage362_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage362_M01J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage365_M00NMJ.jmb",
        ]
        self._Stage_04_Alterego_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage411_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage413_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage413_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage415_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage420_M01J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage421_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage441_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage442_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage444_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage444_M01J.jmb",
        ]
        self._Stage_05_Smile_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage500_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage516_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage517_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage520_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage523_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage524_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage525_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage551_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage551_M01J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage552_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage553_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M01J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M02J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M03J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M04J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M05J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M06J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M07J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M08J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M09J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M10J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M11J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage554_M12J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage555_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage556_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage557_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage557_M00NMJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage559_M00J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/Stage578_M00J.jmb",
        ]
        self._Stage_06_Lion_JA = []

        self._Voice_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/voice01J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/voice02J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/voice03J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/voice04J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/voice05J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/voice06J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/voice07J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/voice08J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/voice09J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/voice10J.jmb",
        ]

        self._System_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/SystemJ.jmb",
        ]

        self._Tutorial_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/tutorial/panelTutorialJ/Stage_tutorialJ.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/tutorial/panelTutorialJ/tutorial_logJ.jmb",
        ]

        self._CharaGeki_US = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00010101/00010101/00010101.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020103/00020103/00020103.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020301/00020301/00020301.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020707/00020707/00020707.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020709/00020709/00020709.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020711/00020711/00020711.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01020203/01020203/01020203.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01030101/01030101/01030101.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050102/01050102/01050102.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01060101/01060101/01060101.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01070202/01070202/01070202.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/02010101/02010101/02010101.jmb",
        ]

        # Combined lists for easy access
        self._CharaGeki_JA    = [
            self._CharaGeki_00_Angel_JA,
            self._CharaGeki_01_Sunset_JA,
            self._CharaGeki_02_Cloudman_JA,
            self._CharaGeki_03_Encounter_JA,
            self._CharaGeki_04_Alterego_JA, # NOTE: 空
            self._CharaGeki_05_Smile_JA,
            self._CharaGeki_06_Lion_JA,
        ]
        self._Zan_JA          = [
            self._Zan_00_Angel_JA,
            self._Zan_01_Sunset_JA,
            self._Zan_02_Cloudman_JA,
            self._Zan_03_Encounter_JA,
            self._Zan_04_Alterego_JA,
            self._Zan_05_Smile_JA,
            self._Zan_06_Lion_JA, # NOTE: 空
            self._Zan_99_Extra_JA,
        ]
        self._Hato_JA         = [
            self._Hato_00_Angel_JA,
            self._Hato_01_Sunset_JA,
            self._Hato_02_Cloudman_JA,
            self._Hato_03_Encounter_JA,
            self._Hato_04_Alterego_JA, # NOTE: 空
            self._Hato_05_Smile_JA,
            self._Hato_06_Lion_JA, # NOTE: 空
        ]
        self._Panel_JA        = [
            self._Panel_00_Angel_JA,
            self._Panel_01_Sunset_JA,
            self._Panel_02_Cloudman_JA,
            self._Panel_03_Encounter_JA,
            self._Panel_04_Alterego_JA,
            self._Panel_05_Smile_JA,
            self._Panel_06_Lion_JA, # NOTE: 空
        ]
        self._Stage_JA        = [
            self._Stage_00_Angel_JA,
            self._Stage_01_Sunset_JA,
            self._Stage_02_Cloudman_JA,
            self._Stage_03_Encounter_JA,
            self._Stage_04_Alterego_JA,
            self._Stage_05_Smile_JA,
            self._Stage_06_Lion_JA, # NOTE: 空
        ]
        self._Movie_JA        = [
            self._Movie_00_Angel_JA, # NOTE: 空
            self._Movie_01_Sunset_JA,
            self._Movie_02_Cloudman_JA,
            self._Movie_03_Encounter_JA, # NOTE: 空
            self._Movie_04_Alterego_JA,
            self._Movie_05_Smile_JA, # NOTE: 空
            self._Movie_06_Lion_JA,
        ]

        self._all_JA_files = {
            "CharaGeki" : self._CharaGeki_JA,
            "Zan" : self._Zan_JA,
            "Hato" : self._Hato_JA,
            "Panel" : self._Panel_JA,
            "Stage" : self._Stage_JA,
            "System" : self._System_JA,
            "Tutorial" : self._Tutorial_JA,
            "Movie" : self._Movie_JA
        }

    def getCharaGeki(self, la: JmkKind) -> list[list[str]]:
        match la:
            case JmkKind.JA:
                return self._CharaGeki_JA
            case JmkKind.US:
                assert False, "no impl"
                # return self._CharaGeki_US
            case _:
                assert False, "unreachable"

    def getZan(self, la: JmkKind) -> list[list[str]]:
        match la:
            case JmkKind.JA:
                return self._Zan_JA
            case JmkKind.US:
                assert False, "no impl"
            case _:
                assert False, "unreachable"

    def getHato(self, la: JmkKind) -> list[list[str]]:
        match la:
            case JmkKind.JA:
                return self._Hato_JA
            case JmkKind.US:
                assert False, "no impl"
            case _:
                assert False, "unreachable"

    def getPanel(self, la: JmkKind) -> list[list[str]]:
        match la:
            case JmkKind.JA:
                return self._Panel_JA
            case JmkKind.US:
                assert False, "no impl"
            case _:
                assert False, "unreachable"

    def getStage(self, la: JmkKind) -> list[list[str]]:
        match la:
            case JmkKind.JA:
                return self._Stage_JA
            case JmkKind.US:
                assert False, "no impl"
            case _:
                assert False, "unreachable"

    def getMovie(self, la: JmkKind) -> list[list[str]]:
        match la:
            case JmkKind.JA:
                return self._Movie_JA
            case JmkKind.US:
                assert False, "no impl"
            case _:
                assert False, "unreachable"

    def getVoice(self, la: JmkKind) -> list[list[str]]:
        match la:
            case JmkKind.JA:
                return self._Voice_JA
            case JmkKind.US:
                assert False, "no impl"
            case _:
                assert False, "unreachable"

    @overload
    @staticmethod
    def flatten_list(nested_list: list[list[str]]) -> list[str]: ...
    @overload
    @staticmethod
    def flatten_list(flat_list: list[str]) -> list[str]: ...
    @staticmethod
    def flatten_list(input_list: Union[list[str], list[list[str]]]) -> list[str]:
        if not input_list:
            return []
        if isinstance(input_list[0], list):
            if not all(isinstance(item, str) for sublist in input_list for item in sublist):
                raise TypeError("Expected list[list[str]] or list[str], got mixed types.")
            return list(itertools.chain.from_iterable(input_list))
        return input_list

    @staticmethod
    def filter(input_list: list[str], rule_set: set[str], reverse: bool = False) -> list[str]:
        if reverse:
            return [p for p in input_list if all(target not in p for target in rule_set)]
        else:
            return [p for p in input_list if any(target in p for target in rule_set)]