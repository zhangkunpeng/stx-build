import os,shutil
import tarfile,re
import log
import time

def get_distro():
    distro = os.environ.get("DISTRO", None)
    if not distro:
        log.critical("Cannot find distro, check env")
    return distro

class BuildManager(object):
    
    def __init__(self, work_path, repo_path, build_type, pkgrepo):
        self.work_path = work_path
        self.repo_path = repo_path
        self.build_type = build_type
        self.pkgrepo = pkgrepo
        self.distro = get_distro()
        self.buildcls = Build.backend(self.distro)
        if not os.path.exists(work_path):
            os.makedirs(work_path)
    
    def pkg_build_list(self):
        pkg_dirs_file = "%s_pkg_dirs" % self.distro
        pkg_list = []
        with open(os.path.join(self.repo_path, pkg_dirs_file)) as f:
            pkg_list = [ line.strip() for line in f.readlines() if line ]
        return pkg_list
    
    def build_pkgs(self):
        for pkg in self.pkg_build_list():
            pkg_path = os.path.join(self.repo_path, pkg)
            work_path = os.path.join(self.work_path, pkg)
            log.info("WORK path: %s" % work_path)
            log.info("PKG Path: %s" % pkg_path)
            if os.path.exists(pkg_path):
                b = self.buildcls(work_path, pkg_path, self.build_type, self.pkgrepo)
                b.prebuild()
                b.build()
            else:
                log.warning("Skip: PKG not exist")

class Build(object):

    DISTRO="None"

    def __init__(self, work_path, pkg_path, build_type):
        self.work_path = work_path
        self.pkg_path = pkg_path
        self.pkg_name = os.path.basename(pkg_path)
        self.verison = ""
        self.platform_release = time.strftime("%y.%m", time.localtime())
        self.pkgrepo_path = pkgrepo
        self.build_type = build_type

    @classmethod
    def backend(cls, distro):
        for c in Build.__subclasses__():
            if c.DISTRO == distro:
                return c
        log.critical("Cannot find build class")

    def prebuild(self):
        log.info("")
        log.info("Start Build: %s" % self.pkg_path)

    def source_files_filter(self, filepath):
        # filepath example:
        # source/centos
        # source/Makefile
        for name in filepath.split("/"):
            if re.match(r'^\.git.*|^build$|^\.pc$|^patches$|^pbr-.*\.egg$', name):
                return False
        if filepath.startswith("sources/centos"):
            return False
        return True
    
    def pkg_name_version(self):
        return "%s-%s" % (self.pkg_name, self.verison)
