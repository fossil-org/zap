class CommandRegistry:
    def __init__(self):
        self.cmds = []
        self.init = False
    def register(self, init = True):
        def register_1(fn):
            self.cmds.append((fn.__name__.replace("_", "-"), fn, init))
            return fn
        return register_1
    def run(self, srcobj, name, args):
        cmd = self.get_command_info(name)
        if cmd["init"] is not None:
            if cmd["init"] and not self.init:
                raise Exception(f"repo must be initialized to use '{name}'")
            if not cmd["init"] and self.init:
                raise Exception(f"repo already initialized.")
        fn = cmd["fn"]
        new_args = []
        from inspect import _empty  # NOQA
        for arg in cmd["args"]:
            from ..src.handle import RaiseError
            new_args.append(srcobj.get_arg(arg["arg"], (lambda: arg["default"]) if arg["default"] is not _empty else RaiseError))
        fn(*new_args)
    def get_command_info(self, name):
        from inspect import signature, _empty # NOQA
        for cmd in self.cmds:
            sig = signature(cmd[1]).parameters.items()
            if cmd[0] == name:
                return {
                    "name": cmd[0],
                    "fn": cmd[1],
                    "init": cmd[2],
                    "help": cmd[1].__doc__,
                    "args": [{"name": k, "arg": f"--{k.replace('_', '-')}", "default": v.default, "help": v.annotation} for k, v in sig]
                }
        else:
            raise Exception(f"unknown command: '{name}'")
    def get_command_help(self, name):
        cmd = self.get_command_info(name)
        cmd_help = f"    {name} - {cmd['help']}:"
        arg_help = []
        from inspect import _empty  # NOQA
        for arg in cmd["args"]:
            arg_help.append(f"      {arg['arg']} ({'required' if arg['default'] is _empty else 'optional'}) - {'no description provided' if arg['help'] is _empty else arg['help']}")
        arg_help = [f"      {cmd['name']} has no parameters."] if not arg_help else arg_help
        return f"{cmd_help}\n{'\n'.join(arg_help)}"