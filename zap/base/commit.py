from pathlib import Path

class Commit:
    def __init__(self, repo, msg, cid, branch, path):
        self.repo = repo
        self.msg = msg
        self.cid = cid
        self.branch = branch
        self.path = Path(path)
        self.path_zap_commit = path / ".zap-commit"
        self.path_zap_commit_cid = self.path_zap_commit / "cid"
        self.path_zap_commit_msg = self.path_zap_commit / "msg"
        self.init()
    def init(self):
        from os import makedirs
        if self.path_zap_commit.exists():
            return
        makedirs(self.path_zap_commit)
        with self.path_zap_commit_cid.open("w") as file:
            file.write(str(self.cid))
        with self.path_zap_commit_msg.open("w") as file:
            file.write(self.msg)
    @classmethod
    def from_existing(cls, repo, cid, branch):
        path = repo.get_branch_path(branch) / str(cid)
        with (path / ".zap-commit" / "msg").open() as file:
            msg = file.read()
        return cls(
            repo,
            msg,
            cid,
            branch,
            path
        )
    def __str__(self):
        return self.to_string()
    def to_string(self, msg_ljust=30):
        return f"{self.msg.ljust(msg_ljust)} | cid: {self.cid.ljust(5)} | branch: {self.branch.ljust(10)} | rb: zap rollback --cid {self.cid} --branch {self.branch}"