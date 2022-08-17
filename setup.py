from cx_Freeze import setup, Executable

copyDependentFiles = True
silent = True
base = None

packages = []
includes = ["re", "os", "psd_tools", "json"]
excludes = ["PyQt4", "PyQt5"]

my_exe = Executable(script="PSDFusionGenerator/PSDFusionGenerator.py", base=base)

setup(
    name="DaVinciResolve_PSDFusionGenerator",
    version="0.1",
    options={
        "build_exe": {"includes": includes, "excludes": excludes, "packages": packages}
    },
    executables=[my_exe],
)
