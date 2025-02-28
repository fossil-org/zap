from pathlib import Path

class Repo:
    def __init__(self, srcobj, path, gh_url):
        self.srcobj = srcobj
        self.storage = Path(__file__).parent.parent / "storage"
        self.path = Path(path)
        self.path_zap = self.path / ".zap"
        self.path_zap_ghm = self.path_zap / "ghm"
        self.path_zap_branches = self.path_zap / "branches"
        self.path_zap_temp = self.path_zap / "temp"
        self.ghm = self.GHM(self, f"{gh_url.removesuffix('.git')}.git")
    @classmethod
    def generate(cls, srcobj, path):
        path = Path(path)
        if not (path / ".zap").exists():
            raise Exception(f"{path} is not a zap repository.")
        with (path / ".zap" / "ghm" / "url").open() as file:
            url = file.read().strip()
        return cls(srcobj, path, url)
    @staticmethod
    def init(path, url):
        from os import mkdir
        path = Path(path)
        if (path / ".zap").exists():
            return
        mkdir(path / ".zap")
        mkdir(path / ".zap" / "ghm")
        with (path / ".zap" / "ghm" / "url").open("w") as file:
            file.write(url)
        mkdir(path / ".zap" / "branches")
        mkdir(path / ".zap" / "branches" / "main")
        mkdir(path / ".zap" / "temp")
    def get_branch_path(self, branch):
        return self.path_zap_branches / branch
    class GHM:
        def __init__(self, repo, url):
            self.repo = repo
            self.url = url
        def runcmd(self, l):
            from subprocess import run, CalledProcessError, PIPE
            from sys import argv
            errors = "--verbose" not in argv
            o = run(l, cwd=str(self.repo.path), capture_output=errors, text=errors)
            if o.returncode != 0:
                self.repo.srcobj.print(f"an unexpected internal error occurred while running '{' '.join(l)}'\ndetails:\n{o.stderr}\n", color="red", title="error")

        def init(self):
            self.runcmd(["rm", "-rf", ".git"])
            self.runcmd(["git", "init"])
            self.runcmd(["git", "checkout", "-b", "main"])
            self.runcmd(["git", "remote", "add", "origin", self.url])
            self.add_all()
            self.commit("initial commit from zap", 0, "main")
            self.runcmd(["git", "push", "--set-upstream", "origin", "main", "-f"])
            self.runcmd(["git", "pull", "--set-upstream", "origin", "main"])
        def add_all(self):
            self.runcmd(["git", "add", "."])
        def pull(self):
            self.runcmd(["git", "pull"])
        def commit(self, msg, cid, branch):
            self.runcmd(["git", "commit", "-m", f"⚡ {msg}", "-m", f"""
this commit was made using zap ⚡
learn more: https://github.com/fossil-org/zap

commit info:
cid: {cid}
branch: {branch}
msg: {msg}
""".strip()])
        def push(self):
            self.runcmd(["git", "push", "--all", "--force"])
        def full_save(self, msg, cid, branch):
            self.pull()
            self.add_all()
            self.commit(msg, cid, branch)
            self.push()
    def get_commit(self, cid, branch):
        from .commit import Commit
        return Commit.from_existing(self, cid, branch)
    def get_commit_path(self, cid, branch):
        return self.get_branch_path(branch) / str(cid)
    def get_commit_msg(self, cid, branch):
        return self.get_commit(cid, branch).msg
    def commit_exists(self, cid, branch):
        return self.get_commit_path(cid, branch).exists()
    @staticmethod
    def ignore(s):
        return lambda dir, files: [s] if s in files else []
    def commit(self, msg, branch):
        from os import makedirs, listdir, mkdir
        from shutil import copytree
        cid = len(listdir(self.get_branch_path(branch))) + 1
        msg = str(cid) if msg is None else msg
        path = Path(self.get_commit_path(cid, branch))
        from .commit import Commit
        copytree(self.path, path, ignore=self.ignore(".zap"))
        makedirs(path, exist_ok=True)
        commit = Commit(
            self,
            msg,
            cid,
            branch,
            path
        )
        self.ghm.full_save(msg, cid, branch)
        return cid
    def list_branches(self):
        from os import listdir
        return listdir(self.path_zap_branches)
    def list_commits_from_branch(self, branch):
        for cid in listdir(self.get_branch_path(branch)):
            l.append(str(Commit.from_existing(self, cid, branch)))
    def list_commits(self, branch = None):
        from os import listdir
        from .commit import Commit
        l = []
        if branch is not None:
            l += self.list_commits_from_branch(branch)
        else:
            for branch in self.list_branches():
                l += self.list_commits_from_branch(branch)
        return l
    def rollback(self, cid, branch, ask=True):
        from shutil import copytree, rmtree
        from os import listdir, remove
        from .commit import Commit
        if not (self.get_branch_path(branch) / cid).exists():
            raise Exception(f"commit {cid} does not exist in branch {branch}")
        commit = Commit.from_existing(self, cid, branch)
        if ask:
            try:
                self.srcobj.print(f"""
are you sure you want to rollback to this commit?
cid: {cid}
msg: {commit.msg}

type 'y' to continue
type 'n' or press <ctrl-c> or <ctrl-d> to cancel
                """.strip(), color="yellow", title="warning")
                while True:
                    i = input("[y/n]: ")
                    if i in ("y", "yes", "ok", "true", "yeah", "continue"):
                        break
                    elif i in ("n", "no", "false", "nope", "cancel"):
                        raise KeyboardInterrupt
            except (KeyboardInterrupt, EOFError):
                self.srcobj.print("rollback cancelled")
                return
        from uuid import uuid4
        temp_item_id = str(uuid4())
        path_temp = self.srcobj.path_temp / temp_item_id
        copytree(self.path_zap, path_temp)
        for item in listdir(self.path):
            if item == ".zap":
                continue
            path = self.path / item
            if path.is_dir():
                rmtree(path)
            else:
                remove(path)
        copytree(commit.path, self.path, ignore=self.ignore(".zap-commit"), dirs_exist_ok=True)
        rmtree(self.path_zap)
        copytree(path_temp, self.path / ".zap", dirs_exist_ok=True)
        rmtree(path_temp)
        self.ghm.full_save(f"[rb] {commit.msg}", f"[rb] {cid}", branch)
        return True
    @classmethod
    def brain(cls, srcobj, args):
        cmd, *args = args
        from os import getcwd
        rg = srcobj.cmdreg.register
        try:
            repo = cls.generate(srcobj, getcwd())
            srcobj.cmdreg.init = True
        except Exception:
            ...
        @rg(init=False)
        def init(url):
            url = f"https://github.com/{url}.git"
            cls.init(getcwd(), url)
            cls.generate(srcobj, getcwd()).ghm.init()
            srcobj.print(f"created zap repository at {getcwd()} linked to git repository at {url}", color="green", title="success")
        @rg()
        def commit(msg = None, branch = "main"):
            cid = repo.commit(msg, branch)
            srcobj.print(f"made new commit on branch {branch}\ncid: {cid}", color="green", title="success")
        @rg()
        def rollback(cid, branch = "main"):
            if repo.rollback(cid, branch):
                srcobj.print(f"rolled back to commit with cid '{cid}'", color="green", title="success")
        @rg()
        def commits(branch = None):
            l = repo.list_commits(branch)
            srcobj.print(f"all commits in {'all branches' if branch is Non else 'branch '+branch}:")
            srcobj.print(*l, sep="\n")
        def branches():
            l = repo.list_branches()
            srcobj.print(f"all branches:")
            srcobj.print(*l, sep="\n")

        srcobj.cmdreg.run(srcobj, cmd, args)