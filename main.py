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
        title="Select PSD File for create Fusion",
        filetypes=[("PSD", ".psd")],
    )
    output_folder_path = os.path.dirname(psd_file_path)
    generator_name = os.path.splitext(os.path.basename(psd_file_path))[0]

    try:
        print("Start PSDFusionGenerator")
        print("Checking PSD #It might takes few min")
        psd_divider = PsdDivider()
        created_folder = psd_divider.execute(psd_file_path, output_folder_path)
        print("Creating .setting")
        setting_creator = SettingCreator()
        setting_creator.execute(created_folder,generator_name)
        messagebox.showinfo("Info", "Create Successful \nCheck Generator in Effects Library")
    except Exception as e:
        messagebox.showerror("Error", "Sometihing error\n" + traceback.format_exc())

__main__()
