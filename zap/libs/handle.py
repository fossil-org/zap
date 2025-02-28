from pathlib import Path
from subprocess import run
from importlib.util import spec_from_file_location, module_from_spec

def init_library(url, add="", gh=True, fossil=True, output=False):
    url = f"fossil-org/{url}" if fossil else url
    url = f"https://github.com/{url}" if gh else url
    name = url.split("/")[-1]
    path = Path(__file__).parent / name
    path_with_add = path / add
    if not path.exists():
        run(["git", "clone", url, str(path)], capture_output=True)
        from colorama import Fore, Style
        print(f"{Fore.LIGHTGREEN_EX}✔ {Style.RESET_ALL}installed zap internal requirement: '{name}'{Style.RESET_ALL}")