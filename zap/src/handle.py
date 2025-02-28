from sys import argv
from pathlib import Path
from ..base.cmdreg import CommandRegistry
from ..base.repo import Repo
from ..libs.handle import init_library
init_library("print", "print/main.py")
from ..libs.print.print import new_console

class RaiseError: ...

console = new_console()

class SRC:
    console = console
    print = console.ppnl
    cmdreg = CommandRegistry()
    path_temp = Path(__file__).parent.parent / "temp"
    @staticmethod
    def get_arg(i_or_str: int | str, else_val = RaiseError):
        if isinstance(i_or_str, int):
            i_or_str += 1
            if i_or_str < len(argv):
                return argv[i_or_str]
            if else_val is not RaiseError:
                return else_val()
            raise Exception("not enough arguments provided.")
        else:
            if i_or_str not in argv[1:]:
                if else_val is not RaiseError:
                    return else_val()
                raise Exception(f"not enough arguments provided; please specify a '{i_or_str}'")
            try:
                return argv[argv.index(i_or_str) + 1]
            except IndexError:
                raise Exception(f"expected a value after '{i_or_str}' argument")
    @staticmethod
    def entrypoint():
        if len(argv) < 2 or argv[1] == "--verbose":
            raise SyntaxError("please specify a command to execute")
        Repo.brain(SRC, argv[1:])
    @staticmethod
    def wrapper(fn, verbose=None):
        if verbose is None:
            verbose = "--verbose" in argv
        try:
            fn()
        except Exception as e:
            if verbose and not isinstance(e, SyntaxError):
                raise e
            SRC.print(f"{e}\nif you believe this is a mistake, please forward this message to maintainers of zap here: "
                      f"https://github.com/fossil-org/zap/issues/new", color="red", title="error")

entrypoint = lambda: SRC.wrapper(SRC.entrypoint)

if __name__ == '__main__':
    entrypoint()