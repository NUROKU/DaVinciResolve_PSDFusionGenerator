import os
import re
import json
from PSDFusionGenerator.Common import common_lib
from psd_tools import PSDImage
from datetime import datetime as dt
from PIL import Image

class PsdDivider:
    # PSD分解してPNGにするやつ
    png_serial_number = 0
    folder_serial_number = 0
    layer_info_dict = {}
    original_info_dict = {}
    input_order_dict = {}

    def execute(self, psd_file_path, output_folder_path, encoding="cp932"):
        # 出力用フォルダ作成、肥大化したらsetup関数作る
        new_folder_name = dt.now().strftime("%Y%m%d_%H%M%S") + "_PFG"
        output_folder_path = output_folder_path + "/" + new_folder_name
        os.makedirs(output_folder_path)

        psd = PSDImage.open(psd_file_path, encoding=encoding)

        depend_group_list = []
        for layer in list(psd.descendants(include_clip=False)):
            if (layer.is_group()):
                # inputのネスト用ラベル生成用、PSDグループの下にPSDグループが存在する場合に親グループ情報保存
                layer_ingroup = list(layer.descendants(include_clip=False))
                is_exist_clip = len([x for x in layer_ingroup if x.kind == "pixel" and x.parent is layer]) != 0
                is_exist_group = len([x for x in layer_ingroup if x.kind == "group"]) != 0
                if (is_exist_group):
                    depend_group_len = len([x for x in layer_ingroup if x.kind == "group"])
                    depend_group_name = common_lib.format_name(layer.name)
                    # レイヤーの有無等で属するグループ数が変わってくるので色々
                    if (is_exist_clip):
                        depend_group_len = depend_group_len + 1
                    for group in [x for x in layer_ingroup if x.kind == "group"]:
                        group_desc = list(group.descendants(include_clip=False))
                        is_exist_clip = len([x for x in group_desc if x.kind == "pixel" and x.parent is group]) != 0
                        is_exist_group = len([x for x in group_desc if x.kind == "group"]) != 0
                        if (is_exist_clip and is_exist_group):
                            depend_group_len = depend_group_len + 1
                    depend_group_list.append([depend_group_name, depend_group_len])
            else:
                # 画像出力して保存するだけ
                folder_path = output_folder_path + "/" + self.output_folder_name(layer)
                self.save_png(layer, folder_path)
                self.store_layer_info(layer, folder_path, depend_group_list)
                depend_group_list = []
        self.add_layer_info(psd)
        self.output_info_json_file(output_folder_path)
        return output_folder_path

    def output_folder_name(self, layer):
        name = common_lib.format_name(layer.parent.name)
        if (layer.parent.parent is not None):
            if (layer.parent.parent.is_group()):
                name = common_lib.format_name(layer.parent.parent.name) + "_" + name
            else:
                name = "Root_" + name
        else:
            # 一番上に画像置いてある場合の処理
            name = "_" + common_lib.format_name(layer.name)
        return name

    def save_png(self, layer, output_folder_path):
        pil_img = layer.topil()
        os.makedirs(output_folder_path, exist_ok=True)
        self.png_serial_number = self.png_serial_number + 1
        if pil_img is None:
            # 0*0画像?で「選択無」パラメータ用意してくれてる立ち絵製作者さんのために
            pil_img = Image.new("RGB", (1, 1), (0, 0, 0))
            pil_img.putalpha(0)
        pil_img.save(
            output_folder_path + "/" + self.output_folder_name(layer) + "-" + str(self.png_serial_number) + ".png"
        )

    def store_layer_info(self, layer, folder_path, depend_group_list):
        # レイヤーの情報を入れたdictを作る、後でsetting作る時の参照先
        layer_info = {
            "size_width": layer.size[0],
            "size_height": layer.size[1],
            "offset_x": layer.offset[0],
            "offset_y": layer.offset[1],
            "layer_name": common_lib.format_name(layer.name),
            "group": common_lib.format_name(layer.parent.name) if layer.parent.parent is not None else os.path.basename(folder_path),
            "group_folder": os.path.basename(folder_path),
            "default_visible": layer.is_visible(),
            "file_path": folder_path + "/" + self.output_folder_name(layer) + "-" + str(self.png_serial_number) + ".png",
            "depend_group_list": depend_group_list
        }
        self.layer_info_dict[str(self.png_serial_number)] = layer_info

    def add_layer_info(self, original_psd):
        # originalのPSD情報
        dict_len = len(self.layer_info_dict)
        self.original_info_dict["size"] = dict_len
        original_width = original_psd.size[0]
        original_height = original_psd.size[1]
        self.original_info_dict["original_psd_size_width"] = original_width
        self.original_info_dict["original_psd_size_height"] = original_height
        # DaVinciResolveでmergeノードのoffsetに入れる値設定
        serial_num = 1
        while True:
            dict = self.layer_info_dict.get(f"{serial_num}")
            if dict is None:
                break

            center_x = round((dict["offset_x"] + (dict["size_width"] / 2)) / original_width,8)
            center_y = round((
                original_height - (dict["offset_y"] + (dict["size_height"] / 2))
            ) / original_height, 8)
            update_dict = {"merge_center_x": center_x, "merge_center_y": center_y}

            self.layer_info_dict[f"{serial_num}"] = {**dict, **update_dict}
            serial_num = serial_num + 1

    def output_info_json_file(self, output_folder_path):
        # 出力するだけ
        common_lib.output_json(output_folder_path + "/psd_layer_info.json", self.layer_info_dict)
        common_lib.output_json(output_folder_path + "/psd_original_info.json", self.original_info_dict)
