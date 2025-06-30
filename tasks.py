import json
import os
import fontTool
import DDSTool
import jmbUtils
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
    Validates that the generated JMB file matches the original file.

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
    for_name = self.context.get('jmb_nmType', False)
    print("\n==== Generate DDS Tex Based on used chars ====")

    if not import_from_file:
        DDSTool.gen(dds_path, unique_chars, fixed_max_width=False, for_name = for_name, original_alignment=False)
    self.jmb.reimport_tex(dds_path)

@basicTask
def TaskGeneratePreview(self:JMBBaseTask):
    """
    Generates preview images of the subtitles.

    Parameters:
        preview_dir (str, required):
            Directory where preview images will be saved.
        extracted_chars_dir (str, optional):
            If provided, uses characters extracted from DDS instead of generating from font.
            When not provided, generates characters from font.
            Default: ""
    """
    extracted_chars_dir = self.params.get('extracted_chars_dir', "")
    depends_on_dds_extraction : bool = (extracted_chars_dir != "")
    preview_dir = self.params.get('preview_dir', 'jmks')
    ctl2char_lookup = self.context.get('ctl2char_lookup', None)
    for_name = self.context.get('jmb_nmType', False)
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
                    break
                # print("\t char_data:", len(jmk.char_data), jmk.char_data)
                # print("\t rubi_data:", len(jmk.rubi_data), jmk.rubi_data)
                target_path = f"{preview_dir}/JA_sent{i}/{jmk_idx:02d}"
                # jmk.dump(target_path)
                if depends_on_dds_extraction:
                    fontTool.save_preview_jimaku(target_path+".png", jmk, fParams=self.jmb.fParams, provided_chars_dir=extracted_chars_dir, for_name=for_name)
                else:
                    fontTool.save_preview_jimaku(target_path+".png", jmk, ctl2char_lookup, for_name=for_name, original_alignment=False)
        else:
            if not sent.valid():
                break
            target_path = f"{preview_dir}/US_sent{i}"
            if depends_on_dds_extraction:
                fontTool.save_preview_jimaku(target_path+".png", sent, fParams=self.jmb.fParams, provided_chars_dir=extracted_chars_dir, for_name=for_name)
            else:
                fontTool.save_preview_jimaku(target_path+".png", sent, ctl2char_lookup, for_name=for_name, original_alignment=False)


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
    default_output_dir = "JMBS/"
    if self.context.get('jmb_zanType'):
        default_output_dir += "Zan/"
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
    translation_dir = "assets/translation/"
    if self.context.get('jmb_zanType'):
        translation_dir += "Zan/"
    default_path = translation_dir + self.context['jmb_name'] + ".json"
    translation_filepath = self.context.get('translation', default_path)
    for_name = self.context.get('jmb_nmType', False)
    assert(os.path.exists(translation_filepath))
    f = open(translation_filepath, 'r', encoding='utf-8')
    translation = json.load(f)
    f.close()
    print("\n==== Modifying Translation ====")

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

    self.jmb.fParams = fontTool.genFParams(unique_chars, for_name=for_name, original_alignment=False)
    self.jmb.update_sentence_ctl(translation, char2ctl_lookup, validation_mode=False)



def run_tasks(input_path:str, tasks:list[type], **task_args):
    task_args['original_path'] = input_path
    jmb_file = os.path.basename(input_path)
    jmb_name = jmb_file[:-4]
    task_args['jmb_file'] = jmb_file
    task_args['jmb_name'] = jmb_name
    task_args['jmb_nmType'] = 'nm' in jmb_name
    task_args['jmb_zanType'] = 'Zan' in input_path
    kind: JmkKind = JmkKind.JA if ('J' in jmb_name) else JmkKind.US

    print(f"\n==== Running Task on {jmb_file} ({kind}) ====")
    jmb = BaseGdat.create(input_path, kind)

    shared_context = {}
    shared_context.update({
        **task_args
    })

    if task_args['provided_text'] != None:
        text = deepcopy(task_args['provided_text'])
        text_flatten = ''.join(t for s in text for t in s)
        ctl2char_lookup, char2ctl_lookup, unique_chars = fontTool.register(text_flatten)

        shared_context.update({
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
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00010101/00010101/00010101J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00010101/00010101/00010101nmJ.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020103/00020103/00020103J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020103/00020103/00020103nmJ.jmb",

        "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/Zan/0071010/0071010J.jmb",

        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/fonts/hato007201J.jmb",

        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020301/00020301/00020301J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020707/00020707/00020707J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020709/00020709/00020709J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/00020711/00020711/00020711J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01020203/01020203/01020203J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01030101/01030101/01030101J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01050102/01050102/01050102J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01060101/01060101/01060101J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/01070202/01070202/01070202J.jmb",
        # "D:/SteamLibrary/steamapps/common/killer7/ReadOnly/CharaGeki/02010101/02010101/02010101J.jmb",



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

        TaskWrapper(TaskGeneratePreview, preview_dir="jmks"),                                   # Generate Previews using registered chars
        # TaskWrapper(TaskGeneratePreview, preview_dir="jmks", extracted_chars_dir = "dds_font"), # Generate Previews using external dir

        TaskSave,                   # write to `JMBS/{jmb_file}` as default
        # TaskWrapper(TaskSave, output_path="testmod.jmb"),
    ]

    tasks_preview_content = [
        TaskValidation,
        TaskWrapper(TaskExtractChars, extracted_dir="dds_font"),
        TaskWrapper(TaskDumpDDSTex, dump_path="DDS_ori.dds"),
        TaskWrapper(TaskGeneratePreview, preview_dir="jmks", extracted_chars_dir = "dds_font"),
    ]
    tasks_test_translation = [
        TaskValidation,
        TaskTranslation,
        TaskWrapper(TaskUpdateTex, import_from_file = False),
        TaskWrapper(TaskGeneratePreview, preview_dir="jmks"),
    ]
    tasks_save_translation = tasks_test_translation + [TaskSave]

    custom = [
        # TaskValidation,
        # TaskPrintFParams,
        TaskFlushFParams,
        TaskWrapper(TaskUpdateTex, import_from_file = False),
        TaskWrapper(TaskDumpDDSTex, dump_path="DDS_mod.dds"),
        TaskWrapper(TaskExtractChars, extracted_dir="modded_dds_font"),
        TaskWrapper(TaskGeneratePreview, preview_dir="jmks"),
    ]

    for file in files:
        jmb_text = None
        text_path = "assets/raw_text/" + os.path.basename(file)[:-4] + ".json"
        if os.path.exists(text_path):
            f = open(text_path, 'r', encoding='utf-8')
            jmb_text = json.load(f)
            f.close()

        run_tasks(
            input_path = file,

            # NOTE: switch between these sets or create your own stuff
            tasks = tasks_preview_content,
            # tasks = tasks_test_translation,
            # tasks = tasks_save_translation,
            # tasks = custom,

            provided_text=jmb_text,
        )