from itertools import groupby
import os
import re
import json
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

        psd = PSDImage.open(psd_file_path,encoding=encoding)

        # psd_list = reversed(list(psd.descendants(include_clip=False)))
        depend_group_list = []
        for layer in list(psd.descendants(include_clip=False)):
            if (layer.is_group()):
                # inputのラベル生成用の処理
                layer_ingroup = list(layer.descendants(include_clip=False))
                is_exist_clip = len([x for x in layer_ingroup if x.kind == "pixel" and x.parent is layer]) != 0
                is_exist_group = len([x for x in layer_ingroup if x.kind == "group"]) != 0
                if (is_exist_group):
                    depend_group_len = len([x for x in layer_ingroup if x.kind == "group"])
                    depend_group_name = self.formatName(layer.name)
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
                folder_path = output_folder_path + "/" + self.outputFolderName(layer)
                self.savePng(layer, folder_path)
                self.storeLayerInfo(layer, folder_path, depend_group_list)
                depend_group_list = []
        self.addLayerInfo(psd)
        self.outputInfojsonFile(output_folder_path)
        return output_folder_path

    def formatName(self, text: str):
        # 文字化け対応
        text = text.encode("utf-16", "surrogatepass").decode("utf-16")

        # フォルダ作成時の禁止用語コンバート
        text = re.sub(r'[\\/:*?"<>| ]+', "_", text)
        text = text.replace("\x00", "")
        if text == "":
            text = "_"
        return text

    def outputFolderName(self, layer):
        name = self.formatName(layer.parent.name)
        # self.folder_serial_number = self.folder_serial_number + 1
        if (layer.parent.parent is not None):
            if (layer.parent.parent.is_group()):
                name = self.formatName(layer.parent.parent.name) + "_" + name
            else:
                name = "Root_" + name
        else:
            # 一番上に画像置いてある場合の処理
            name = "_" + self.formatName(layer.name)
        return name

    def savePng(self, layer, output_folder_path):
        pil_img = layer.topil()
        os.makedirs(output_folder_path, exist_ok=True)
        # ここに画像サイズ縮小処理とか入れれそう、いれてないけど
        self.png_serial_number = self.png_serial_number + 1
        if pil_img is None:
            # 0*0画像?で「選択無」パラメータ用意してくれてる立ち絵製作者さんのために
            pil_img = Image.new("RGB", (1, 1), (0, 0, 0))
            pil_img.putalpha(0)
        pil_img.save(
            output_folder_path + "/" + self.outputFolderName(layer) + "-" + str(self.png_serial_number) + ".png"
        )

    def storeLayerInfo(self, layer, folder_path, depend_group_list):
        # レイヤーの情報を入れたdictを作る、後でsetting作る時の参照先
        layer_info = {
            "size_width": layer.size[0],
            "size_height": layer.size[1],
            "offset_x": layer.offset[0],
            "offset_y": layer.offset[1],
            "layer_name": self.formatName(layer.name),
            "group": self.formatName(layer.parent.name) if layer.parent.parent is not None else os.path.basename(folder_path),
            "group_folder": os.path.basename(folder_path),
            "default_visible": layer.is_visible(),
            "file_path": folder_path + "/" + self.outputFolderName(layer) + "-" + str(self.png_serial_number) + ".png",
            "depend_group_list": depend_group_list
        }
        self.layer_info_dict[str(self.png_serial_number)] = layer_info

    def addLayerInfo(self, original_psd):
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

    def outputInfojsonFile(self, output_folder_path):
        # 出力するだけ
        with open(
            output_folder_path + "/psd_layer_info.json", "w", encoding="utf-8_sig"
        ) as f:
            json.dump(self.layer_info_dict, f, indent=2, ensure_ascii=False)
        with open(
            output_folder_path + "/psd_original_info.json", "w", encoding="utf-8_sig"
        ) as f:
            json.dump(self.original_info_dict, f, indent=2, ensure_ascii=False)
