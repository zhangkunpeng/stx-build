__all__ = ['rpm', 'CentosBuild']

from stxbuild.common import build, log, git, patch
from stxbuild.common.context import Context
import os, shutil
import rpm

class CentosBuild(build.Build):
    DISTRO = "centos"

    def __init__(self, context):
        super(CentosBuild, self).__init__(context)
        self.ctxt.distro_repo = os.path.join(context.mirror, "cgcs-centos-repo")
        self.ctxt.third_party = os.path.join(context.mirror, "cgcs-3rd-party-repo")
        self.ctxt.output = os.path.join(context.mirror, self.ctxt.build_type, "rpmbuild")

    def perpare_build(self, ctxt):
        ctxt.TIS_DIST = self.ctxt.TIS_DIST
        ctxt.distro_dir = os.path.join(ctxt.pkgdir, self.DISTRO)
        self.find_build_mode(ctxt)
        self.find_build_data(ctxt)
        self.find_pkg_name_ver(ctxt)
        self.perpare_workdir(ctxt)


    def execute_build(self, ctxt):
        self.perpare_source(ctxt)
        self.compile(ctxt)


    def after_build(self, ctxt):
        self.copy_to_output(ctxt)
        rpm.update_repodata(ctxt.output)
        rpm.yum_clean_cache()
        rpm.yum_makecache()

    def find_build_mode(self, ctxt):
        srpm_path = os.path.join(ctxt.pkgdir, "%s/srpm_path" % self.DISTRO)

        def orig_srpm_path(line):
            if line.startswith("/"):
                filepath = line
            elif line.startswith("repo:"):
                # TODO 暂时未发现repo，遇到后再补充
                filepath = line.replace("repo:",self.ctxt.mirror+"/",1)
            elif line.startswith("3rd_party:"):
                filepath = line.replace("3rd_party:",self.ctxt.third_party+"/",1)
            elif line.startswith("mirror:"):
                filepath = line.replace("mirror:",self.ctxt.distro_repo+"/",1)\
                                .replace("CentOS/tis-r3-CentOS/kilo/","")\
                                .replace("CentOS/tis-r3-CentOS/mitaka/","")
            else:
                filepath = self.ctxt.distro_repo+"/"+line
            if os.path.exists(filepath):
                return filepath
            log.error("Invalid srpm path '%s', evaluated as '%s', found in '%s'" % (line, filepath, srpm_path))

        if os.path.exists(srpm_path):
            with open(srpm_path) as f:
                for line in f.readlines():
                    ctxt.orig_srpm_path = orig_srpm_path(line.strip())
                    ctxt.build_mode = "srpm"
        
        spec_path = os.path.join(ctxt.pkgdir, self.DISTRO)
        for filename in os.listdir(spec_path):
            if filename.endswith(".spec"):
                ctxt.orig_sepc_path = os.path.join(spec_path, filename)
                ctxt.build_mode = "spec"
        
        #ctxt.workdir = os.path.join(self.ctxt.workdir, ctxt.build_mode, self.pkg)
        if ctxt.orig_sepc_path and ctxt.orig_srpm_path:
            log.error("Please provide only one of srpm_path or .spec files, not both, in '%s'" % spec_path)
        if not ctxt.orig_sepc_path and not ctxt.orig_srpm_path:
            log.error("Please provide only one of srpm_path or .spec files, not None, in '%s'" % spec_path)

    def find_build_data(self, ctxt):
        build_srpm_data = os.path.join(ctxt.pkgdir, "centos/build_srpm.data")
        if not os.path.exists(build_srpm_data):
            log.error("%s not found" % build_srpm_data)
        for line in open(build_srpm_data):
            line = line.strip()
            log.debug("build_srpm.data: %s" % line)
            r = line.split("=")
            if len(r) == 2:
                ctxt[r[0]] = r[1].strip("\'\"")
        
        if not ctxt.TIS_PATCH_VER:
            log.error("TIS_PATCH_VER must be set in %s" % build_srpm_data)
        if ctxt.TIS_PATCH_VER.startswith("GITREVCOUNT"):
            if not ctxt.TIS_BASE_SRCREV:
                log.error("TIS_BASE_SRCREV must be set in %s" % build_srpm_data)
            items = ctxt.TIS_BASE_SRCREV.split("+")
            count = 0 if len(items) == 1 else int(items[1])
            count = count + git.commit_count(ctxt) + git.plus_by_status(ctxt)
            ctxt.TIS_PATCH_VER = str(count)
        
    def find_pkg_name_ver(self, ctxt):
        if ctxt.orig_srpm_path:
            ctxt.name = rpm.query_srpm_name(ctxt.orig_srpm_path)
            ctxt.version = rpm.query_srpm_version(ctxt.orig_srpm_path)
            ctxt.release = rpm.query_srpm_release(ctxt.orig_srpm_path)
            ctxt.fullname = "%s-%s-%s" % (ctxt.name, ctxt.version, ctxt.release)
        if ctxt.orig_sepc_path:
            pass

    def perpare_workdir(self, ctxt):
        ctxt.workdir = os.path.join(self.ctxt.workdir, ctxt.build_mode, ctxt.fullname)
        ctxt.build_dir = os.path.join(ctxt.workdir, "rpmbuild")
        if os.path.exists(ctxt.workdir):
            shutil.rmtree(ctxt.workdir)
        os.makedirs(ctxt.build_dir)

    def perpare_source(self, ctxt):
        if ctxt.orig_srpm_path:
            rpm.srpm_extract(ctxt)
        if ctxt.orig_sepc_path:
            pass
        patch.apply_meta_patches(ctxt)
        patch.add_other_patches(ctxt)
        patch.add_other_files(ctxt)
        self.find_spec_file(ctxt)
        # ctxt.release = rpm.query_spec_release(ctxt, ctxt.specfile)
        rpm.build_srpm(ctxt, self.ctxt.platform_release, self.ctxt.build_type)
        self.find_srpm_file(ctxt)
        ctxt.release = rpm.query_srpm_release(ctxt.srpmfile)
        
    def find_spec_file(self, ctxt):
        specdir = os.path.join(ctxt.build_dir, "SPECS")
        for filename in os.listdir(specdir):
            if filename.endswith(".spec"):
                ctxt.specfile = os.path.join(specdir, filename)
                log.info("find out spec file: %s" % ctxt.specfile)
        if not ctxt.specfile:
            log.error("Can not find out a spec file")

    def find_srpm_file(self, ctxt):
        srpmdir = os.path.join(ctxt.build_dir, "SRPMS")
        for filename in os.listdir(srpmdir):
            if filename.endswith(".src.rpm"):
                ctxt.srpmfile = os.path.join(srpmdir, filename)
                log.info("find out srpm file: %s" % ctxt.srpmfile)
        if not ctxt.srpmfile:
            log.error("Can not find out a srpm file")

    def compile(self, ctxt):
        rpm.install_build_dependence(ctxt.srpmfile)
        rpm.build_rpm(ctxt, self.ctxt.platform_release)

    def copy_to_output(self, ctxt):
        self.mkdirs(self.ctxt.output)
        log.info("copy %s to %s" % (ctxt.srpmfile, self.ctxt.output))
        ctxt.rpmdir = os.path.join(ctxt.build_dir, "RPMS")
        ctxt.rpmfiles = [ os.path.join(ctxt.rpmdir, filename) \
                            for filename in os.listdir(ctxt.rpmdir) \
                            if filename.endswith(".rpm")]
        for rpmfile in ctxt.rpmfiles + [ctxt.srpmfile]:
            shutil.copy2(rpmfile, self.ctxt.output)
            log.info("copy %s to %s" % (rpmfile, self.ctxt.output))
