import os,shutil
from git import Repo
from git import RemoteProgress
import log
import progressbar

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
            self.repo.create_head(branch)
        elif self.url.startswith("http"):
            if not path:
                path = self.path
            if os.path.exists(path):
                shutil.rmtree(path)
            self.repo = Repo.clone_from(url=self.url,to_path=path, depth=1, branch=branch, progress=MyProgressPrinter())
        else:
            log.error("Cannot get repo")

class MyProgressPrinter(RemoteProgress):
    p = progressbar.ProgressBar()
    def __init__(self):
        super(MyProgressPrinter, self).__init__()
        self.p = progressbar.ProgressBar(max_value=100)
        
    def update(self, op_code, cur_count, max_count=None, message=''):
        self.p.max_value = max_count or 100
        self.p.update(cur_count)
# end
