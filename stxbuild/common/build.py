import os,shutil
import tarfile,re
import log
import time
from context import Context
from subprocess import CalledProcessError

def get_distro():
    distro = os.environ.get("DISTRO", None)
    if not distro:
        log.critical("Cannot find distro, check env")
    return distro

class Build(object):

    DISTRO="None"

    def __new__(cls, *args, **kwargs):
        for c in Build.__subclasses__():
            if c.DISTRO == get_distro():
                return object.__new__(c, *args, **kwargs)
        return object.__new__(cls, *args, **kwargs)

    def __init__(self, context):
        self.ctxt = context
        self.ctxt.distro = self.DISTRO
        self.distdir = context.distdir
        self.workdir = context.workdir
        self.ctxt.platform_release = time.strftime("%y.%m", time.localtime())
        self.pkg = None

    def package_list(self):
        for filename in ["%s_pkg_dirs" % self.DISTRO, "pkg_dirs"]:
            filepath = os.path.join(self.distdir, filename)
            if os.path.exists(filepath):
                with open(filepath) as f:
                    return [ line.strip() for line in f.readlines() if line ]
        log.error("Can not find out package list")

    def build(self):
        pkglist = self.package_list()
        tobuildlist = pkglist
        
        while tobuildlist:
            build_success_list = []
            for pkg in tobuildlist:
                self.pkg = pkg
                pkg_path = os.path.join(self.distdir, pkg)
                if not os.path.exists(pkg_path):
                    log.warning("Skip: PKG %s not exist" % pkg_path)
                    continue
                log.info("****** Source: %s ==> WORK: %s" % (pkg_path,self.workdir))
                try:
                    self.ctxt[pkg] = Context()
                    self.ctxt[pkg].pkgdir = pkg_path
                    #self.ctxt[pkg].workdir = work_path
                    self.perpare_build(self.ctxt[pkg])
                    self.execute_build(self.ctxt[pkg])
                    self.after_build(self.ctxt[pkg])
                    build_success_list.append(pkg)
                except CalledProcessError as perr:
                    log.warning("Pkg %s build error" % pkg_path)
                    log.warning(perr.output)
            if not build_success_list:
                log.error("no pkgs were build successfully this turn")
            tobuildlist = [ x for x in tobuildlist if x not in build_success_list]

    def perpare_build(self, ctxt):
        pass

    def execute_build(self, ctxt):
        pass

    def after_build(self, ctxt):
        pass

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

    def mkdirs(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
