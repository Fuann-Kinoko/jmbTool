import itertools
from typing import Union, overload
from jmbData import JmkKind

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
        self._Hato_00_Angel_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato007201J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato007301J.jmb",
        ]
        self._Movie_01_Sunset_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/Movie/01010101/01010101.jmb",
        ]
        self._Panel_00_Angel_JA = [
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P000304J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P000501J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P000603J.jmb",
            "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P007201J.jmb",
        ]
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
        ]
        self._Zan_JA          = [
            self._Zan_00_Angel_JA,
            self._Zan_01_Sunset_JA,
        ]
        self._Hato_JA         = [self._Hato_00_Angel_JA]
        self._Panel_JA        = [self._Panel_00_Angel_JA]
        self._Stage_JA        = [self._Stage_00_Angel_JA]
        self._Movie_JA        = [self._Movie_01_Sunset_JA]

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
    def filter(input_list: list[str], rule_set: set[str]) -> list[str]:
        return list(
            p for p in input_list
            if any(target in p for target in rule_set)
        )