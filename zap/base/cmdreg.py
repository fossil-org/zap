class CommandRegistry:
    def __init__(self):
        self.cmds = []
        self.init = False
    def register(self, init = True):
        def register_1(fn):
            self.cmds.append((fn.__name__, fn, init))
            return fn
        return register_1
    def run(self, srcobj, name, args):
        for cmd in self.cmds:
            if cmd[0] == name:
                if cmd[2] and not self.init:
                    raise Exception(f"repo must be initialized to use '{name}'")
                if not cmd[2] and self.init:
                    raise Exception(f"repo already initialized.")
                fn = cmd[1]
                from inspect import signature, _empty # NOQA
                sig = signature(fn).parameters.items()
                new_args = []
                for arg_name, arg in sig:
                    from ..src.handle import RaiseError
                    new_args.append(srcobj.get_arg(f"--{arg_name}", (lambda: arg.default) if arg.default is not _empty else RaiseError))
                fn(*new_args)
                break
        else:
            raise Exception(f"unknown command: '{name}'")