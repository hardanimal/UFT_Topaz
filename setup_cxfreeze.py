import sys
sys.path.append('src')
from cx_Freeze import setup, Executable

includes = ["UFT", "UFT_GUI"]

if sys.platform == "win32":
    base = "Win32GUI"
else:
    base = None

exe = Executable(script="src/UFT_GUI/main.py", base=base)

setup(
    name="UFT Topaz GUI",
    version="2.3",
    options={"build_exe": {"includes": includes,
                           }
             },
    executables=[exe],
    )
