from . import jmbConst
from copy import deepcopy

def display_char_data(lst: list[int]) -> list[int]:
    try:
        first_neg2_index = lst.index(-2)
    except ValueError:
        print("ERROR: lst =", lst)
        raise ValueError("no RET in char data")

    # 检查第一个-2右边的所有元素是否都是-1
    right_part = lst[first_neg2_index+1:]
    if not all(x == -1 for x in right_part):
        print("Error List:")
        print(lst)
        raise ValueError("There should be no Valid Char after RET")

    return lst[:first_neg2_index]

def print_jmt_differences(original: list[list[str]]|None, modified: list[list[str]]):
    if original is None:
        for sent_idx, mod_sent in enumerate(modified):
            for line_idx, mod_line in enumerate(mod_sent):
                print(f"(*) DIFFERENCE at [{sent_idx},{line_idx}]:")
                print(f"    Original: {'(not provided)'}")
                print(f"    Modified: {mod_line or '(none)'}\n")
        return
    any_difference = False
    for sent_idx in range(max(len(original), len(modified))):
        orig_sent = original[sent_idx] if sent_idx < len(original) else []
        mod_sent = modified[sent_idx] if sent_idx < len(modified) else []
        for line_idx in range(max(len(orig_sent), len(mod_sent))):
            # 获取当前行
            orig_line = orig_sent[line_idx] if line_idx < len(orig_sent) else None
            mod_line = mod_sent[line_idx] if line_idx < len(mod_sent) else None

            # 检查是否不同
            if orig_line != mod_line:
                any_difference = True
                print(f"(*) DIFFERENCE at [{sent_idx},{line_idx}]:")
                print(f"    Original: {orig_line or '(none)'}")
                print(f"    Modified: {mod_line or '(none)'}\n")
    if not any_difference:
        print("No differences found.")

def translation_correction(translation: list[list[str]], usage: jmbConst.JmkUsage) -> list[list[str]]:
    ret_translation = deepcopy(translation)
    for sent_idx, sent in enumerate(ret_translation):
        for jmk_idx, jimaku in enumerate(sent):
            new_str = ""
            for idx, char in enumerate(jimaku):
                cur_char = char
                if char == "杀":
                    cur_char = "殺"
                if char == "?":
                    cur_char = "？"
                if char == "!":
                    cur_char = "！"
                if usage == jmbConst.JmkUsage.Hato:
                    if char == "，":
                        cur_char = ","
                    if char == "。":
                        cur_char = "."
                new_str += cur_char
            ret_translation[sent_idx][jmk_idx] = new_str

    return ret_translation