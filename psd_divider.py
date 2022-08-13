import os
import re
import json
from psd_tools import PSDImage
from datetime import datetime as dt
from PIL import Image

class PsdDivider:
    # PSD分解してPNGにするやつ
    png_serial_number = 0
    layer_info_dict = {}
    original_info_dict = {}
    input_order_dict = {}

    def execute(self, psd_file_path, output_folder_path, encoding="cp932"):
        # 出力用フォルダ作成、肥大化したらsetup関数作る
        new_folder_name = dt.now().strftime("%Y%m%d_%H%M%S") + "_psdtool"
        output_folder_path = output_folder_path + "/" + new_folder_name
        os.makedirs(output_folder_path)

        psd = PSDImage.open(psd_file_path,encoding=encoding)

        # psd_list = reversed(list(psd.descendants(include_clip=False)))
        depend_group = []
        for layer in list(psd.descendants(include_clip=False)):
            if (layer.is_group()):
                #em = next(filter(lambda x: x[0] == layer.parent, depend_group), None)
                #if (em is not None):
                #    em[1] = em[1] + 1

                l = list(layer.descendants(include_clip=False))
                depend_group.append([self.outputFolderName(layer), len([x for x in l if x.kind == "group"])])
                #is_exist_clip = len([x for x in layer_ingroup if x.kind == "pixel"]) != 0
                #is_exist_group = len([x for x in layer_ingroup if x.kind == "group"]) != 0
                #if (is_exist_clip and is_exist_group):
                #    depend_group.append([layer, 1, self.png_serial_number])
                #else:
                #    depend_group.append([layer, 0, self.png_serial_number])
                
            else:
                folder_path = output_folder_path + "/" + self.outputFolderName(layer)
                self.savePng(layer, folder_path)
                self.storeLayerInfo(layer, folder_path)
        self.addLayerInfo(psd)
        self.addInputOrder(depend_group)
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
        if (layer.parent.parent is not None):
            if (layer.parent.parent.is_group()):
                name = self.formatName(layer.parent.parent.name) + "-" + name
        else:
            # 一番上に画像置いてある場合の処理
            name = name + self.formatName(layer.name)
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
            output_folder_path + "/" + self.outputFolderName(layer) + str(self.png_serial_number) + ".png"
        )

    def storeLayerInfo(self, layer, folder_path):
        # レイヤーの情報を入れたdictを作る、後でsetting作る時の参照先
        layer_info = {
            "size_width": layer.size[0],
            "size_height": layer.size[1],
            "offset_x": layer.offset[0],
            "offset_y": layer.offset[1],
            "layer_name": self.formatName(layer.name),
            "group": os.path.basename(folder_path),
            "default_visible": layer.is_visible(),
            "file_path": folder_path + "/" + self.outputFolderName(layer) + str(self.png_serial_number) + ".png",
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

    def addInputOrder(self, depend_group):
        pass
        # layer_info_dictをグループ順にまとめて、間にトグル入れてく
        # 作成中、
        # index = 0
        # loader_index = 0
        # for key, group in groupby(self.layer_info_dict, key=lambda m: m['group']):
        #     index = index + 1
        #     loader_index = loader_index + 1
        #     self.input_order_dict[str(index)] = {
        #         "name": "Loader" + str(index),
        #         "type": "Loader",
        #         "loader_index": loader_index,
        #         "num_inputs": 0
        #     }
        #     
        #     group_list = list(group)
        #     parent_layer = group_list[0][1].parent
        #     parent_depend_group = [x for x in depend_group if x[0] == parent_layer][0]
        #     if (parent_depend_group is not None):
        #         if (parent_depend_group[1] != 0):
        #             index = index + 1
        #             self.input_order_dict[str(index)] = {
        #                 "name": parent_depend_group.name,
        #                 "type": "Label",
        #                 "loader_index": loader_index,
        #                 "num_inputs": parent_depend_group[1] 
        #             }                   
        # print(self.input_order_dict)
        
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
