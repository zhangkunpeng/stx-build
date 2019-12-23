import os, tarfile,re,shutil
import build
import subprocess
import log
import json

class RpmBuild(build.Build):

    DISTRO = "centos"
    
    def __init__(self, work_path, pkg_path, build_type):
        super(RpmBuild, self).__init__(work_path, pkg_path, build_type)
        self.distro = "centos"
        self.source_path = os.path.join(work_path, "SOURCES")
        self.spec_path = os.path.join(work_path, "SPECS")
        self.srpm_path = os.path.join(work_path, "SRPMS")
        self.rpm_path = os.path.join(work_path, "RPMS")
        self.build_srpm_data = {}
        self.SRC_DIR = None
        self.EXCLUDE_FILES_FROM_TAR = None
        self.TIS_PATCH_VER = None
        self.rpmrepo_path = "/tmp/centos/rpm"
        self.srpmrepo_path = "/tmp/centos/srpm"

    def read_build_srpm_data(self):
        for line in open(os.path.join(self.pkg_path, self.distro, "build_srpm.data")):
            line = line.strip()
            log.debug("build_srpm.data: %s" % line)
            r = line.split("=")
            if len(r) == 2:
                self.build_srpm_data[r[0]] = r[1].strip("\'\"")
        self.SRC_DIR = self.build_srpm_data.get("SRC_DIR")
        self.EXCLUDE_FILES_FROM_TAR = self.build_srpm_data.get("EXCLUDE_FILES_FROM_TAR")
        self.TIS_PATCH_VER = self.build_srpm_data.get("TIS_PATCH_VER")

    def copy_spec(self):
        self.mkdirs(self.spec_path)
        for root, dirs, files in os.walk(os.path.join(self.pkg_path, self.distro)):
            for filename in files:
                if filename.endswith(".spec"):
                    dist_spec_file = os.path.join(self.spec_path, filename)
                    shutil.copy(os.path.join(root, filename), dist_spec_file)
                    self.modify_spec(dist_spec_file)
    
    def modify_spec(self, spec_file):
        lines = []
        with open(spec_file, 'r') as f:
            for l in f:
                lines.append(l)
        lines.insert(0, "%%define _tis_build_type %s\n" % self.build_type)
        lines.insert(0, "%%define tis_patch_ver %s\n" % self.TIS_PATCH_VER)
        with open(spec_file, 'w') as f:
            f.write(''.join(lines))

    def read_pkg_version(self):
        def __read_pkg_version_from_spec():
            for root, dirs, files in os.walk(os.path.join(self.pkg_path, self.distro)):
                for filename in files:
                    if filename.endswith(".spec"):
                        for line in open(os.path.join(root, filename)):
                            r = re.search(r'^Version: (\d.*)', line)
                            if r:
                                return r.group(1)
        self.verison = __read_pkg_version_from_spec()
        if not self.verison:
            print("Cannot find version")
            exit(1)
        self.pkg_name_version = "%s-%s" % (self.pkg_name, self.verison)

    def tar_sources(self):
        self.mkdirs(self.source_path)
        tar_name = "%s.tar.gz" % self.pkg_name_version
        tar = tarfile.open(os.path.join(self.source_path, tar_name), "w:gz")
        for root, dirs, files in os.walk(os.path.join(self.pkg_path,self.SRC_DIR)):
            for filename in files:
                abspath = os.path.join(root, filename)
                relpath = os.path.relpath(abspath, self.pkg_path)
                if self.source_files_filter(relpath):
                    arcname = os.path.join(self.pkg_name_version, os.path.relpath(relpath, self.SRC_DIR))
                    tar.add(name=abspath,arcname=arcname)
        tar.close()

    def prebuild(self):
        super(RpmBuild, self).prebuild()
        self.read_build_srpm_data()
        self.read_pkg_version()
        self.tar_sources()
        self.copy_spec()
        self.mkdirs(self.srpm_path)
        self.mkdirs(self.rpm_path)
        log.debug(self.__dict__)

    def install_dependence(self, specfile):
        if not os.path.exists(os.path.join(self.rpmrepo_path, "repodata/repomd.xml")):
            self.update_repodata()
        subprocess.check_call(["/usr/bin/yum-builddep", specfile])

    def build_srpm(self, specfile):
        command = ["/usr/bin/rpmbuild","-bs",specfile, 
                    "--undefine=dist", 
                    "--define=%%_topdir %s" % self.work_path,
                    "--define=_tis_dist .tis"]
        log.info(" ".join(command))
        subprocess.check_call(command)
    
    def build_rpm(self, srpmfile):
        command = ["/usr/bin/rpmbuild","--rebuild",srpmfile, 
                    "--define=platform_release %s" % self.platform_release,
                    "--define=%%_topdir %s" % self.work_path,
                    "--define=_tis_dist .tis"]
        log.info(" ".join(command))
        subprocess.check_call(command)

    def install_rpm(self, rpmfile):
        command = ["/usr/bin/rpm","-ivh",rpmfile]
        log.info(" ".join(command))
        subprocess.call(command)

    def copy_to_repo(self, rpmfile=None, srpmfile=None):
        self.mkdirs(self.rpmrepo_path)
        self.mkdirs(self.srpmrepo_path)
        if rpmfile:
            shutil.copy2(rpmfile, self.rpmrepo_path)
        if srpmfile:
            shutil.copy2(srpmfile, self.srpmrepo_path)

    def update_repodata(self):
        for repo in [self.rpmrepo_path, self.srpmrepo_path]:
            self.mkdirs(repo)
            command = ["/usr/bin/createrepo","--update",repo]
            log.info(" ".join(command))
            subprocess.check_call(command)
        subprocess.check_call(["/usr/bin/yum", "clean", "all"])
        subprocess.check_call(["/usr/bin/yum", "makecache"])

    def build(self):
        for root,dirs,files in os.walk(self.spec_path):
            for filename in files:
                if filename.endswith(".spec"):
                    spec_file = os.path.join(root, filename)
                    self.install_dependence(spec_file)
                    self.build_srpm(spec_file)
        for root,dirs,files in os.walk(self.srpm_path):
            for filename in files:
                if filename.endswith(".src.rpm"):
                    srpmfile = os.path.join(root, filename)
                    self.build_rpm(srpmfile)
                    self.copy_to_repo(srpmfile=srpmfile)

        for root,dirs,files in os.walk(self.rpm_path):
            for filename in files:
                if filename.endswith(".rpm"):
                    rpmfile = os.path.join(root, filename)
                    self.install_rpm(rpmfile)
                    self.copy_to_repo(rpmfile=rpmfile)
        #self.update_repodata()
        