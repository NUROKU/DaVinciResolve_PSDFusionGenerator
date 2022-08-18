from itertools import groupby
import json
import os
from PSDFusionGenerator.SettingCreator.template_const import TemplateConst

class SettingCreator():

    psd_layer_dict = None
    psd_original_dict = None
    generator_macro_path = "C:/ProgramData/Blackmagic Design/DaVinci Resolve/Fusion/Templates/Edit/Generators"

    # 1. template_constから作成する.settingの変換前文字列取得
    # 2. 置換したい変換前の文字:変換後の文字 のdict作成
    # 3. replace_wordsで変換
    # という流れをMergeノードLoaderノードetc...全部でやってる。
    # 正直Base_settingみたいな基底クラス作って継承クラスinput_setting,merge_setting...って対応した方がいいと思う
    # 気が向けれたらやる

    def execute(self, psdtool_folder:str, setting_file_name:str):

        # psd_info読み込み
        self.psd_layer_dict = json.load(open(psdtool_folder + '/psd_layer_info.json', 'r', encoding="utf-8_sig"))
        self.psd_layer_dict = sorted(self.psd_layer_dict.items(), key=lambda x:int(x[0]))

        self.psd_original_dict = json.load(open(psdtool_folder + '/psd_original_info.json', 'r', encoding="utf-8_sig"))
        content = self.create_main_content()

        os.makedirs(self.generator_macro_path, exist_ok=True)
        with open(f"{self.generator_macro_path}/{setting_file_name}.setting", 'w', encoding="utf-8") as f:
            f.write(content)

    def replace_words(self, original_text: str, replace_dict: dict):
        txt = original_text
        for re_from, re_to in replace_dict.items():
            txt = txt.replace(str(re_from), str(re_to))
        return txt

    def create_main_content(self):
        replace_dict = {
            "%%%INPUT_CONTENT%%%": self.create_input_content(),
            "%%%LOADER_CONTENT%%%": self.create_loader_content(),
            "%%%BACKGROUND_CONTENT%%%": self.create_background_content(),
            "%%%MEDIAOUT_CONTENT%%%": self.create_output_content(),
            "%%%MERGE_CONTENT%%%": self.create_merge_content()
        }

        return self.replace_words(TemplateConst.MAIN_CONTENT,replace_dict)

    def create_input_content(self):
        input_content = ""
        key_count = 0
        group_label_count = 0
        for key, group in groupby(self.psd_layer_dict, key=lambda m: m[1]['group']):
            group_list = list(group)
            if (group_list[0][1]["depend_group_list"] is not []):
                splited_group = group_list[0][1]["depend_group_list"]
                for group in splited_group:
                    group_label_count = group_label_count + 1
                    # ネスト追加処理
                    group_replace_dict = {
                        "%%%NODE_NAME%%%": "nest_label" + str(group_label_count),
                        "%%%SOURCE_GROUP_NAME%%%": "nest_label" + str(group_label_count),
                    }
                    input_content = input_content + self.replace_words(TemplateConst.INPUT_CONTENT_GROUP_PARTS,group_replace_dict)                

            replace_dict = {
                "%%%NODE_NAME%%%": "",
                "%%%SOURCE_NAME%%%": "",
            }
            key_count = key_count + 1
            replace_dict["%%%NODE_NAME%%%"] = "input" + str(key_count)
            replace_dict["%%%SOURCE_NAME%%%"] = "Loader" + str(key_count)
            input_content = input_content + self.replace_words(TemplateConst.INPUT_CONTENT_PARTS, replace_dict)
        return input_content

    def create_loader_content(self):
        def framerender_script(merge_node_name, max_val):
            return f"if self.image_selector < {max_val} then\\n    self.ClipTimeStart = self.image_selector\\n    self.ClipTimeEnd = self.image_selector\\n    index = self.image_selector + 1\\n    {merge_node_name}.Center.X = cft[index][1]\\n    {merge_node_name}.Center.Y = cft[index][2]\\nelse\\n    {merge_node_name}.Center.X = -1\\n    {merge_node_name}.Center.Y = -1\\nend"
        loader_content = ""
        key_count = 0
        for key, group in groupby(self.psd_layer_dict, key=lambda m: m[1]['group']):
            replace_dict = {
                "%%%NODE_NAME%%%": "",
                "%%%CLIP_ID%%%": "",
                "%%%CLIP_FILE_PATH%%%": "",
                "%%%CLIP_START_FRAME%%%": "",
                "%%%CLIP_LENGTH%%%": 0,
                "%%%SCRIPT_COMMENT%%%": "",
                "%%%FRAMERANDER_SCRIPT%%%": "",
                "%%%STARTRENDER_SCRIPT%%%": "",
                "%%%IMAGE_SELECTOR_SELECT%%%": -1,
                "%%%NODE_POS_X%%%": 0,
                "%%%NODE_POS_Y%%%": 0,
                "%%%LAYER_GROUP_NAME%%%": "",
                "%%%MAX_NUM_LENGTH%%%": 0,
                "%%%CSS_ADD_STRING_LIST%%%": ""
            }
            key_count = key_count + 1
            group_list = list(group)
            replace_dict["%%%NODE_NAME%%%"] = "Loader" + str(key_count)
            replace_dict["%%%CLIP_ID%%%"] = str(key)
            replace_dict["%%%CLIP_FILE_PATH%%%"] = group_list[0][1]["file_path"].replace("/","\\\\")
            replace_dict["%%%CLIP_START_FRAME%%%"] = str(group_list[0][0])
            replace_dict["%%%CLIP_LENGTH%%%"] = len(group_list)
            replace_dict["%%%SCRIPT_COMMENT%%%"] = "v0.1"
            replace_dict["%%%FRAMERANDER_SCRIPT%%%"] = framerender_script("PSDMerge" + str(key_count),len(group_list))
            def_count = 0
            for g in group_list:
                if g[1]["default_visible"] is True:
                    replace_dict["%%%IMAGE_SELECTOR_SELECT%%%"] = def_count
                    break
                def_count = def_count + 1
            if replace_dict["%%%IMAGE_SELECTOR_SELECT%%%"] == -1:
                def_count = def_count + 1
                replace_dict["%%%IMAGE_SELECTOR_SELECT%%%"] = def_count
            replace_dict["%%%NODE_POS_X%%%"] = key_count * 110 
            replace_dict["%%%NODE_POS_Y%%%"] = 50
            replace_dict["%%%LAYER_GROUP_NAME%%%"] = str(key)
            replace_dict["%%%MAX_NUM_LENGTH%%%"] = len(group_list) - 1
            replace_dict["%%%STARTRENDER_SCRIPT%%%"] = "cft = {}"
            g_count = 0
            for g in group_list:
                replace_dict["%%%STARTRENDER_SCRIPT%%%"] = replace_dict["%%%STARTRENDER_SCRIPT%%%"] + "\\ncft[" + str(g_count + 1) + "] = {}"
                replace_dict["%%%STARTRENDER_SCRIPT%%%"] = replace_dict["%%%STARTRENDER_SCRIPT%%%"] + "\\ncft[" + str(g_count + 1) + "][1] = " + str(g[1]["merge_center_x"])
                replace_dict["%%%STARTRENDER_SCRIPT%%%"] = replace_dict["%%%STARTRENDER_SCRIPT%%%"] + "\\ncft[" + str(g_count + 1) + "][2] = " + str(g[1]["merge_center_y"])
                replace_dict["%%%CSS_ADD_STRING_LIST%%%"] = replace_dict["%%%CSS_ADD_STRING_LIST%%%"] + "    							{ CCS_AddString = \"" + g[1]["layer_name"] + "\" }," + "\n"
                g_count = g_count + 1
            replace_dict["%%%CSS_ADD_STRING_LIST%%%"] = replace_dict["%%%CSS_ADD_STRING_LIST%%%"] + "    							{ CCS_AddString = \"\" },"
            loader_content = loader_content + self.replace_words(TemplateConst.LOADER_CONTENT_PARTS,replace_dict)
        return loader_content

    def create_background_content(self):
        replace_dict = {
            "%%%SIZE_WIDTH%%%": "",
            "%%%SIZE_HEIGHT%%%": "",
            "%%%NODE_POS_X%%%": 0,
            "%%%NODE_POS_Y%%%": 0,
            "%%%LABEL_CONTENT%%%": ""
        }
        replace_dict["%%%SIZE_WIDTH%%%"] = str(self.psd_original_dict["original_psd_size_width"])
        replace_dict["%%%SIZE_HEIGHT%%%"] = str(self.psd_original_dict["original_psd_size_height"])
        replace_dict["%%%NODE_POS_X%%%"] = -110 
        replace_dict["%%%NODE_POS_Y%%%"] = 0

        group_label_count = 0
        for key, group in groupby(self.psd_layer_dict, key=lambda m: m[1]['group']):
            group_list = list(group)
            if (group_list[0][1]["depend_group_list"] is not []):
                splited_group = group_list[0][1]["depend_group_list"]
                for group in splited_group:
                    group_label_count = group_label_count + 1
                    label_replace_dict = {
                        "%%%GROUP_LABEL_NAME%%%": "nest_label" + str(group_label_count),
                        "%%%LAYER_PARENT_GROUP_NAME%%%": group[0],
                        "%%%LAYER_PARENT_NUM_INPUTS%%%": group[1],
                    }
                    replace_dict["%%%LABEL_CONTENT%%%"] = replace_dict["%%%LABEL_CONTENT%%%"] + self.replace_words(TemplateConst.BACKGROUND_LABEL_CONTENT_PARTS,label_replace_dict)

        return self.replace_words(TemplateConst.BACKGROUND_CONTENT,replace_dict)

    def create_merge_content(self):
        merge_content = ""
        replace_dict = {
            "%%%NODE_NAME%%%": "",
            "%%%BACKGROUND_SOURCE%%%": "",
            "%%%FOREGROUND_SOURCE%%%": "",
            "%%%NODE_POS_X%%%": 0,
            "%%%NODE_POS_Y%%%": 0,
        }
        key_count = 0
        for key, group in groupby(self.psd_layer_dict, key=lambda m: m[1]['group']):
            key_count = key_count + 1
            replace_dict["%%%NODE_NAME%%%"] = "PSDMerge" + str(key_count)
            if key_count == 1:
                replace_dict["%%%BACKGROUND_SOURCE%%%"] = "Background1"
            else:
                replace_dict["%%%BACKGROUND_SOURCE%%%"] = "PSDMerge" + str(key_count - 1)
            replace_dict["%%%FOREGROUND_SOURCE%%%"] = "Loader" + str(key_count)
            replace_dict["%%%NODE_POS_X%%%"] = key_count * 110 
            replace_dict["%%%NODE_POS_Y%%%"] = 0
            merge_content = merge_content + self.replace_words(TemplateConst.MERGE_CONTENT_PARTS,replace_dict)

        return merge_content

    def create_output_content(self):
        replace_dict = {
            "%%%SOURCE_OP%%%": "",
            "%%%NODE_POS_X%%%": 0,
            "%%%NODE_POS_Y%%%": 0,
        }
        key_count = 0
        for key, group in groupby(self.psd_layer_dict, key=lambda m: m[1]['group']):
            key_count = key_count + 1
        replace_dict["%%%SOURCE_OP%%%"] = "PSDMerge" + str(key_count)
        replace_dict["%%%NODE_POS_X%%%"] = (key_count+1) * 110
        return self.replace_words(TemplateConst.OUTPUT_CONTENT,replace_dict)