import json
import os
import fontTool
import DDSTool
import jmbUtils
import jmbConst
from jmbData import BaseGdat, JmkKind, gDat, gDat_JA

from copy import copy, deepcopy
import unittest
from unittest import TestCase

class JMBBaseTask(TestCase):
    jmb : gDat
    context : dict = {}
    params : dict = {}

    @classmethod
    def set_context(cls, jmb: gDat, shared_context: dict):
        cls.jmb = jmb
        cls.context = shared_context

    def runTest(self):
        self.execute()

    def execute(self):
        raise NotImplementedError("Subclasses must implement execute()")

class TaskWrapper:
    def __init__(self, task_cls, **params):
        self.task_cls = task_cls
        self.params = params

class JMBTestLoader(unittest.TestLoader):
    def __init__(self, jmb : gDat = None, shared_context: dict = None):
        super().__init__()
        self.jmb = jmb
        self.shared_context = shared_context or {}

    def loadTestsFromTaskWrapper(self, task_wrapper: TaskWrapper):
        task_cls = task_wrapper.task_cls
        if issubclass(task_cls, JMBBaseTask):
            task_cls.set_context(self.jmb, self.shared_context)
            test_case = task_cls()
            test_case.params = task_wrapper.params
            return test_case
        else:
            self.loadTestsFromTestCase(task_cls)

    def loadTestsFromTestCase(self, testCaseClass):
        if issubclass(testCaseClass, JMBBaseTask):
            testCaseClass.set_context(self.jmb, self.shared_context)
        return super().loadTestsFromTestCase(testCaseClass)

def basicTask(func):
    class Task(JMBBaseTask):
        def execute(self):
            return func(self)
    Task.__name__ = func.__name__
    Task.__doc__ = func.__doc__
    return Task

def check_raw_text_prepared(ctx: dict):
    ready = True
    ready &= (ctx.get('unique_chars') != None)
    ready &= (ctx.get('ctl2char_lookup') != None)
    ready &= (ctx.get('char2ctl_lookup') != None)
    assert ready, (
        "if not ready:\n"
        "1. Read raw text (e.g., `assets/raw_text/00010101J.json`)\n"
        "2. Call `fontTool.register`\n"
        "3. Manually update the context"
    )

@basicTask
def TaskValidation(self:JMBBaseTask):
    """
    测试读取后，根据其生成的jmb是否能跟原文件一样
    Validates that the loaded JMB file matches the original file.

    Parameters:
        None
    """
    original_path = self.context['original_path']
    print("\n==== Validation ====")

    result = self.jmb.no_diff_with(original_path)
    print(f"Validation Result: {result}")
    if not result:
        self.fail("Validation failed!")

@basicTask
def TaskUpdateTex(self:JMBBaseTask):
    """
    测试读取使用的字符后，重新生成自己的DDS Tex，能否成功
    Updates DDS texture based on used characters.

    Parameters:
        import_from_file (bool, optional):
            If True, imports characters from an existing DDS file.
            If False, generates new characters from font.
            Default: False
        import_path (str, optional):
            Path to the DDS file to import when import_from_file is True.
            Default: 'gen.dds'
    """
    import_from_file: bool = self.params.get('import_from_file', False)
    if not import_from_file:
        check_raw_text_prepared(self.context)
    dds_path: str = self.params.get('import_path', 'gen.dds')
    unique_chars = self.context.get('unique_chars')
    usage = self.context.get('jmb_usage', 0)
    print("\n==== Generate DDS Tex Based on used chars ====")

    if not import_from_file:
        DDSTool.gen(dds_path, unique_chars, usage, fixed_max_width=False, original_alignment=False)
    self.jmb.reimport_tex(dds_path)

@basicTask
def TaskGeneratePreview(self:JMBBaseTask):
    """
    Generates preview images of the subtitles.

    Parameters:
        preview_dir (str, required):
            Directory where preview images will be saved.
        seperate_by_jmbname (bool, optional):
            Whether the generated preview will be write into a seperate folder
            Default: False
        extracted_chars_dir (str, optional):
            If provided, uses characters extracted from DDS instead of generating from font.
            When not provided, generates characters from font.
            Default: ""
    """
    extracted_chars_dir = self.params.get('extracted_chars_dir', "")
    depends_on_dds_extraction : bool = (extracted_chars_dir != "")
    seperate_by_jmbname : bool = self.params.get('seperate_by_jmbname', False)
    preview_dir = self.params.get('preview_dir', 'jmks')
    if seperate_by_jmbname:
        jmb_name = self.context['jmb_name']
        preview_dir += f"/{jmb_name}"
    ctl2char_lookup = self.context.get('ctl2char_lookup', None)
    usage = self.context.get('jmb_usage', 0)
    if not depends_on_dds_extraction:
        check_raw_text_prepared(self.context)
    print("\n==== Generating Previews ====")

    assert(self.jmb.meta.sentence_num == len(self.jmb.sentences))
    for i in range(self.jmb.meta.sentence_num):
        sent = self.jmb.sentences[i]
        print(f"generating preview for sentence {i}")
        if isinstance(self.jmb, gDat_JA):
            for jmk_idx, jmk in enumerate(sent.jimaku_list):
                if not jmk.valid():
                    print(f"\thas {jmk_idx} valid jimakus")
                    break
                # print("\t char_data:", len(jmk.char_data), jmk.char_data)
                # print("\t rubi_data:", len(jmk.rubi_data), jmk.rubi_data)
                target_path = f"{preview_dir}/JA_sent{i}/{jmk_idx:02d}"
                # jmk.dump(target_path)
                if depends_on_dds_extraction:
                    fontTool.save_preview_jimaku(target_path+".png", jmk, usage, fParams=self.jmb.fParams, provided_chars_dir=extracted_chars_dir)
                else:
                    fontTool.save_preview_jimaku(target_path+".png", jmk, usage, ctl2char_lookup, original_alignment=False)
        else:
            if not sent.valid():
                break
            target_path = f"{preview_dir}/US_sent{i}"
            if depends_on_dds_extraction:
                fontTool.save_preview_jimaku(target_path+".png", sent, usage, fParams=self.jmb.fParams, provided_chars_dir=extracted_chars_dir)
            else:
                fontTool.save_preview_jimaku(target_path+".png", sent, usage, ctl2char_lookup, original_alignment=False)


@basicTask
def TaskExtractChars(self:JMBBaseTask):
    """
    Extracts characters from DDS texture.

    Parameters:
        extracted_dir (str, optional):
            Directory where extracted characters will be saved.
            Default: 'modded_dds_font'
    """
    extracted_dir = self.params.get('extracted_dir', 'modded_dds_font')
    print("\n==== Extracting Chars From DDS ====")

    DDSTool.extract(extracted_dir, self.jmb.tex.dds, self.jmb.fParams, should_store = True)

@basicTask
def TaskDumpDDSTex(self:JMBBaseTask):
    """
    Dumps the DDS texture to a file.

    Parameters:
        dump_path (str, optional):
            Path where the DDS file will be saved.
            Default: 'gen.dds'
    """
    dump_path = self.params.get('dump_path', 'gen.dds')
    print(f"\n==== Dump DDS to {dump_path} ====")

    self.jmb.tex.dump(dump_path)

@basicTask
def TaskPrintMetaData(self:JMBBaseTask):
    """
    Prints the JMB file's metadata.

    Parameters:
        None
    """
    print("\n==== Printing MetaData ====")
    print(self.jmb.meta)

@basicTask
def TaskPrintRegisteredChars(self:JMBBaseTask):
    """
    Prints information about registered characters.

    Parameters:
        None
    """
    check_raw_text_prepared(self.context)
    unique_chars = self.context['unique_chars']
    ctl2char_lookup = self.context['ctl2char_lookup']
    char2ctl_lookup = self.context['char2ctl_lookup']
    print("\n==== Printing Registered Chars ====")

    print("+unique_chars:", unique_chars)
    print("+ctl2char:", ctl2char_lookup)
    print("+char2ctl:", char2ctl_lookup)

@basicTask
def TaskFlushFParams(self:JMBBaseTask):
    """
    Prints font parameters.

    Parameters:
        None
    """
    print("\n==== Flushing FParams ====")
    self.jmb.flush_fparams()
    print("Finished.")

@basicTask
def TaskPrintFParams(self:JMBBaseTask):
    """
    Prints font parameters.

    Parameters:
        None
    """
    print("\n==== Printing FParams ====")
    for param in self.jmb.fParams:
        print(param)

@basicTask
def TaskPrintDDSInfo(self:JMBBaseTask):
    """
    Prints information about the DDS texture.

    Parameters:
        None
    """
    print("\n==== Printing DDS Info ====")
    print("tex_offset =", self.jmb.meta.tex_offset)
    print("header =", self.jmb.tex.header)
    DDSTool.print_info(self.jmb.tex.dds)
    if isinstance(self.jmb, gDat_JA):
        print("jmb after_tex_pos =", self.jmb.meta.s_motion_offset)

@basicTask
def TaskSave(self:JMBBaseTask):
    """
    单纯的保存为文件
    Saves the modified JMB file.

    Parameters:
        output_path (str, optional):
            Path where the modified JMB file will be saved.
            Default: 'testmod.jmb'
    """
    default_output_dir = "JMBS/" + self.context.get('jmb_output_prefix', "")
    jmb_name = self.context['jmb_name']
    output_path = self.params.get('output_path', default_output_dir + f'{jmb_name}.jmb')
    print("\n==== Saving Modified File ====")

    self.jmb.write_to_file(output_path)
    print(f"File saved to: {output_path}")

@basicTask
def TaskTranslation(self:JMBBaseTask):
    """
    修改一部分文字
    """
    translation_dir = "assets/translation/" + self.context.get('jmb_output_prefix', "")
    default_path = translation_dir + self.context['jmb_name'] + ".json"
    translation_filepath = self.context.get('translation', default_path)
    usage = self.context.get('jmb_usage', 0)
    assert(os.path.exists(translation_filepath))
    f = open(translation_filepath, 'r', encoding='utf-8')
    translation = json.load(f)
    f.close()
    print("\n==== Modifying Translation ====")

    translation = jmbUtils.translation_correction(translation, usage)
    jmbUtils.print_jmt_differences(self.context.get('provided_text'), translation)

    text_flatten = ''.join(t for s in translation for t in s)
    ctl2char_lookup, char2ctl_lookup, unique_chars = fontTool.register(text_flatten)
    self.context.update({
        'text': translation,
        'text_flatten': text_flatten,
        'ctl2char_lookup': ctl2char_lookup,
        'char2ctl_lookup': char2ctl_lookup,
        'unique_chars': unique_chars
    })

    print(f'translation updated; unique_chars = "{unique_chars}"')

    self.jmb.fParams = fontTool.genFParams(unique_chars, usage, original_alignment=False)
    self.jmb.update_sentence_ctl(translation, char2ctl_lookup, validation_mode=False)



def run_tasks(input_path:str, tasks:list[type], **task_args):
    task_args['original_path'] = input_path
    jmb_file = os.path.basename(input_path)
    jmb_name = jmb_file[:-4]
    task_args['jmb_file'] = jmb_file
    task_args['jmb_name'] = jmb_name

    usage = jmbConst.JmkUsage.Default
    if 'nm' in jmb_name or 'NM' in jmb_name:
        assert usage == jmbConst.JmkUsage.Default
        usage = jmbConst.JmkUsage.Name
    if 'hato' in jmb_name:
        assert usage == jmbConst.JmkUsage.Default
        usage = jmbConst.JmkUsage.Hato
    task_args['jmb_usage'] = usage

    if 'Zan' in input_path:
        task_args['jmb_output_prefix'] = 'Zan/'
    if 'hato' in jmb_name:
        task_args['jmb_output_prefix'] = 'hato/'
    if 'Movie' in input_path:
        task_args['jmb_output_prefix'] = 'Movie/'
    if 'fonts' in input_path and 'P' in jmb_name:
        task_args['jmb_output_prefix'] = 'Panel/'
    if 'fonts' in input_path and 'Stage' in jmb_name:
        task_args['jmb_output_prefix'] = 'Stage/'
    if 'fonts' in input_path and 'System' in jmb_name:
        task_args['jmb_output_prefix'] = 'System/'
    kind = JmkKind.US
    if 'J' in jmb_name or ('Movie' in input_path and 'E' not in jmb_name):
        kind: JmkKind = JmkKind.JA
    print(f"\n==== Running Task on {jmb_file} ({kind}) ====")
    jmb = BaseGdat.create(input_path, kind)

    shared_context = {}
    shared_context.update({
        **task_args
    })


    raw_text_path = "assets/raw_text/" + task_args.get('jmb_output_prefix', "") + jmb_name + ".json"
    if os.path.exists(raw_text_path):
        f = open(raw_text_path, 'r', encoding='utf-8')
        text = json.load(f)
        f.close()
        text_flatten = ''.join(t for s in text for t in s)
        ctl2char_lookup, char2ctl_lookup, unique_chars = fontTool.register(text_flatten)

        shared_context.update({
            'provided_text' : text,
            'text': text,
            'text_flatten': text_flatten,
            'ctl2char_lookup': ctl2char_lookup,
            'char2ctl_lookup': char2ctl_lookup,
            'unique_chars': unique_chars,
        })

    loader = JMBTestLoader(jmb=jmb, shared_context = shared_context)

    suite = unittest.TestSuite()
    for task in tasks:
        if isinstance(task, TaskWrapper):
            suite.addTest(loader.loadTestsFromTaskWrapper(task))
        else:
            assert(issubclass(task, JMBBaseTask))
            suite.addTest(loader.loadTestsFromTestCase(task))

    runner = unittest.TextTestRunner(failfast=True)
    runner.run(suite)

if __name__ == '__main__':
    files = [
        # JA
        ## CharaGeki
        ### 00: Angel
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

        ### 01: Sunset
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01020203/01020203/01020203J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01030101/01030101/01030101J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050102/01050102/01050102J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01060101/01060101/01060101J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01070202/01070202/01070202J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/02010101/02010101/02010101J.jmb",

        ## Zan
        ### 00: Angel
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

        ## Hato
        ### 00: Angel
        "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato007201J.jmb",
        "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato007301J.jmb",

        ## Movie
        ### 01: Sunset
        # "D:/SteamLibrary/steamapps/common/killer7/Movie/01010101/01010101.jmb",

        ## Panel
        ### 00: Angel
        "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P000304J.jmb",
        "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P000501J.jmb",
        "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P000603J.jmb",
        "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/P007201J.jmb",

        ## Stage
        ### 00: Angel
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


        ## System
        "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/SystemJ.jmb"


        # US
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00010101/00010101/00010101.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020103/00020103/00020103.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020301/00020301/00020301.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020707/00020707/00020707.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020709/00020709/00020709.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020711/00020711/00020711.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01020203/01020203/01020203.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01030101/01030101/01030101.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050102/01050102/01050102.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01060101/01060101/01060101.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01070202/01070202/01070202.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/02010101/02010101/02010101.jmb",
        # 似乎不存在的英文字符：Q X Z
    ]

    tasks = [
        TaskPrintMetaData,
        # TaskPrintRegisteredChars, # Only Avaliable if there's raw text provided (e.g. `assets/raw_text/00010101J.json`)
        TaskPrintFParams,
        TaskPrintDDSInfo,

        TaskValidation,

        TaskWrapper(TaskExtractChars, extracted_dir="dds_font"),
        TaskWrapper(TaskDumpDDSTex, dump_path="DDS_ori.dds"),

        TaskTranslation,            # trying to find `assets/translation/{jmb_name}.json` as default

        # TaskWrapper(TaskUpdateTex, import_from_file = True, dds_path = 'gen.dds'),    # Update by external DDS
        TaskWrapper(TaskUpdateTex, import_from_file = False),                           # Update by registered chars (translation / raw text)

        TaskWrapper(TaskDumpDDSTex, dump_path="DDS_mod.dds"),
        TaskWrapper(TaskExtractChars, extracted_dir="modded_dds_font"),

        TaskWrapper(TaskGeneratePreview, seperate_by_jmbname=False, preview_dir="jmks"),                                   # Generate Previews using registered chars
        # TaskWrapper(TaskGeneratePreview, preview_dir="jmks", extracted_chars_dir = "dds_font"), # Generate Previews using external dir

        TaskSave,                   # write to `JMBS/{jmb_file}` as default
        # TaskWrapper(TaskSave, output_path="testmod.jmb"),
    ]

    tasks_preview_content = [
        TaskPrintMetaData,
        TaskValidation,
        TaskWrapper(TaskExtractChars, extracted_dir="dds_font"),
        TaskWrapper(TaskDumpDDSTex, dump_path="DDS_ori.dds"),
        TaskWrapper(TaskGeneratePreview, seperate_by_jmbname=True, preview_dir="jmks", extracted_chars_dir = "dds_font"),
    ]
    tasks_test_translation = [
        TaskValidation,
        TaskTranslation,
        TaskWrapper(TaskUpdateTex, import_from_file = False),
        TaskWrapper(TaskGeneratePreview, seperate_by_jmbname=True, preview_dir="jmks"),
    ]
    tasks_save_translation = [
        TaskValidation,
        TaskTranslation,
        TaskWrapper(TaskUpdateTex, import_from_file = False),
        # TaskWrapper(TaskGeneratePreview, seperate_by_jmbname=True, preview_dir="jmks"),
        TaskSave
    ]

    custom = [
        TaskValidation,
        TaskPrintFParams,
        # TaskFlushFParams,
        # TaskWrapper(TaskUpdateTex, import_from_file = False),
        # TaskWrapper(TaskDumpDDSTex, dump_path="DDS_mod.dds"),
        # TaskWrapper(TaskExtractChars, extracted_dir="modded_dds_font"),
        # TaskWrapper(TaskGeneratePreview, preview_dir="jmks"),
    ]

    for file in files:
        run_tasks(
            input_path = file,

            # NOTE: switch between these sets or create your own stuff
            tasks = tasks_preview_content,
            # tasks = tasks_test_translation,
            # tasks = tasks_save_translation,
            # tasks = custom,
        )