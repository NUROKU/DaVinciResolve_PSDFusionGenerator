import os
from tkinter import filedialog, messagebox
from psd_tools import PSDImage
from psd_divider import PsdDivider
from setting_creator import SettingCreator
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

    psd_divider = PsdDivider()
    created_folder = psd_divider.execute(psd_file_path, output_folder_path)
    setting_creator = SettingCreator()
    setting_creator.execute(created_folder,generator_name)
    #
    messagebox.showinfo("報告", "DaVinciResolveに取り込めました。\nEditページ→エフェクト→ジェネレーター→Fusionジェネレーターにあります")

__main__()
