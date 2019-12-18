import os
from git import Repo
from git import RemoteProgress
import log

class RepoManager(object):

    def __init__(self, url, path):
        self.url = url
        self.repo = None
        self.repo_name = os.path.basename(path)
        self.path = path

    def checkout(self, path=None, branch="master"):
        log.info("fetch repo: %s branch: %s" % (self.url, branch))
        if os.path.isdir(self.url):
            self.repo = Repo(path)
        elif os.path.islink(self.url):
            if not path:
                path = self.path
            self.repo = Repo.clone_from(url=self.url,to_path=path, depth=1, branch=branch, progress=MyProgressPrinter())

class MyProgressPrinter(RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        log.info(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE")
# end
