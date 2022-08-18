import os
from tkinter import filedialog, messagebox
import traceback
from PSDFusionGenerator.PSDDivider.psd_divider import PsdDivider
from PSDFusionGenerator.SettingCreator.setting_creator import SettingCreator
import tkinter as tk

def __main__():
    root = tk.Tk()
    root.withdraw()
    psd_file_path = filedialog.askopenfilename(
        title="DaVinci Resolveで使用したいPSDファイルを選択してください",
        filetypes=[("PSD", ".psd")],
    )
    output_folder_path = os.path.dirname(psd_file_path)
    generator_name = os.path.splitext(os.path.basename(psd_file_path))[0]

    try:
        print("PSDFusionGeneratorを開始します。")
        print("PSDを解析中です。（これには数十秒かかる場合があります）")
        psd_divider = PsdDivider()
        created_folder = psd_divider.execute(psd_file_path, output_folder_path)
        print("settingファイルを作成中です")
        setting_creator = SettingCreator()
        setting_creator.execute(created_folder,generator_name)
        messagebox.showinfo("報告", "DaVinciResolveに取り込めました。\nEditページ→エフェクト→ジェネレーター→Fusionジェネレーターにあります")
    except Exception as e:
        messagebox.showerror("エラー", "DavinciResolveに取り込めませんでした。\n" + traceback.format_exc())

__main__()
