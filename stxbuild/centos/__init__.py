__all__ = ['rpm', 'CentosBuild']

from stxbuild.common import build, log, shell, utils
from stxbuild.common.context import Context
import os, shutil, json
import rpm

class CentosBuild(build.Build):
    DISTRO = "centos"

    def __init__(self, context):
        super(CentosBuild, self).__init__(context)
        self.ctxt.distro_repo = os.path.join(context.mirror, "cgcs-centos-repo")
        self.ctxt.third_party = os.path.join(context.mirror, "cgcs-3rd-party-repo")
        self.ctxt.output = os.path.join(context.mirror, self.ctxt.build_type, "rpmbuild/RPMS")
        self.mkdirs(self.ctxt.output)
        log.info(json.dumps(self.ctxt, indent=4))

    def perpare_build(self, ctxt):
        ctxt.TIS_DIST = self.ctxt.TIS_DIST
        ctxt.distro_dir = os.path.join(ctxt.pkgdir, self.DISTRO)
        self.find_build_mode(ctxt)
        self.find_build_data(ctxt)
        self.find_pkg_name_ver(ctxt)
        self.perpare_workdir(ctxt)
        log.info(json.dumps(ctxt, indent=4))

    def execute_build(self, ctxt):
        self.perpare_source(ctxt)
        self.compile(ctxt)
        log.info(json.dumps(ctxt, indent=4))

    def after_build(self, ctxt):
        self.copy_to_output(ctxt)
        rpm.update_repodata(self.ctxt.output)
        rpm.yum_clean_cache()
        rpm.yum_makecache()
        log.info(json.dumps(ctxt, indent=4))

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
        if ctxt.orig_sepc_path and ctxt.orig_srpm_path:
            log.error("Please provide only one of srpm_path or .spec files, not both, in '%s'" % spec_path)
        if not ctxt.orig_sepc_path and not ctxt.orig_srpm_path:
            log.error("Please provide only one of srpm_path or .spec files, not None, in '%s'" % spec_path)

    def find_build_data(self, ctxt):
        ctxt.build_srpm_data = os.path.join(ctxt.pkgdir, "%s/build_srpm.data" % self.DISTRO)
        if not os.path.exists(ctxt.build_srpm_data):
            log.error("%s not found" % ctxt.build_srpm_data)
        for line in open(ctxt.build_srpm_data):
            line = line.strip()
            log.debug("build_srpm.data: %s" % line)
            r = line.split("=")
            if len(r) == 2:
                ctxt[r[0]] = r[1].strip("\'\"")
        
        if not ctxt.TIS_PATCH_VER:
            log.error("TIS_PATCH_VER must be set in %s" % ctxt.build_srpm_data)
        if ctxt.TIS_PATCH_VER.startswith("GITREVCOUNT"):
            if not ctxt.TIS_BASE_SRCREV:
                log.error("TIS_BASE_SRCREV must be set in %s" % ctxt.build_srpm_data)
            items = ctxt.TIS_PATCH_VER.split("+")
            count = 0 if len(items) == 1 else int(items[1]) + \
                    shell.git_commit_count(ctxt.pkgdir,ctxt.TIS_BASE_SRCREV) + \
                    shell.git_plus_by_status(ctxt.pkgdir)
            ctxt.TIS_PATCH_VER = str(count)
        ctxt.FILES_BASE = "%s/files" % self.DISTRO
        ctxt.CGCS_BASE = self.ctxt.distro_repo
        
    def find_pkg_name_ver(self, ctxt):
        if ctxt.orig_srpm_path:
            ctxt.name = rpm.query_srpm_tag(ctxt.orig_srpm_path, "Name")
            ctxt.version = rpm.query_srpm_tag(ctxt.orig_srpm_path, "Version")
            ctxt.release = rpm.query_srpm_tag(ctxt.orig_srpm_path, "Release")
            ctxt.fullname = "%s-%s-%s" % (ctxt.name, ctxt.version, ctxt.release)
        if ctxt.orig_sepc_path:
            ctxt.name = rpm.query_spec_tag(ctxt, "Name")
            ctxt.version = rpm.query_spec_tag(ctxt, "Version")
            ctxt.release = rpm.query_spec_tag(ctxt, "Release")
        ctxt.fullname = "%s-%s-%s" % (ctxt.name, ctxt.version, ctxt.release)
        # log.error("TODO spec")

    def perpare_workdir(self, ctxt):
        ctxt.workdir = os.path.join(self.ctxt.workdir, ctxt.build_mode, ctxt.fullname)
        ctxt.build_dir = os.path.join(ctxt.workdir, "rpmbuild")
        ctxt.build_spec_dir = os.path.join(ctxt.build_dir, "SPECS")
        ctxt.build_srpm_dir = os.path.join(ctxt.build_dir, "SRPMS")
        ctxt.build_rpm_dir = os.path.join(ctxt.build_dir, "RPMS")
        ctxt.build_src_dir = os.path.join(ctxt.build_dir, "SOURCES")
        if os.path.exists(ctxt.workdir):
            shutil.rmtree(ctxt.workdir)
        self.mkdirs(ctxt.build_dir)
        self.mkdirs(ctxt.build_src_dir)
        self.mkdirs(ctxt.build_spec_dir)

    def perpare_source(self, ctxt):
        if ctxt.orig_srpm_path:
            rpm.srpm_extract(ctxt)
        if ctxt.orig_sepc_path:
            pass
        self.apply_meta_patches(ctxt)
        self.copy_additional_patch(ctxt)
        self.copy_additional_src(ctxt)
        ctxt.specfiles = utils.find_out_files(ctxt.build_spec_dir, ".spec")
        # ctxt.release = rpm.query_spec_release(ctxt, ctxt.specfile)
        rpm.build_srpm(ctxt, self.ctxt.platform_release, self.ctxt.build_type)
        ctxt.srpmfiles = utils.find_out_files(ctxt.build_srpm_dir, ".src.rpm")
        ctxt.release = rpm.query_srpm_tag(ctxt.srpmfiles[0], "Release")

    def copy_additional_src(self, ctxt):
        # 复制额外的source 到 rpmbuild/SOURCES
        # example:
        #   files/*
        #   centos/files/*
        #   ${CGCS_BASE}/downloads/XXXX.tar.gz
        if ctxt.COPY_LIST:
            ctxt.copy_path_list = shell.echo_env(ctxt, "COPY_LIST").split(" ")
            if not ctxt.copy_path_list:
                log.error(" [%s] ctxt.copy_path_list not exist" % ctxt.name)
        ctxt.build_src_dir = os.path.join(ctxt.build_dir, "SOURCES")
        self.mkdirs(ctxt.build_src_dir)
        for p in ctxt.copy_path_list:
            p = p[:-2] if p.endswith("/*") else p
            p = p if os.path.isabs(p) else os.path.join(ctxt.pkgdir, p)
            utils.copy(p, ctxt.build_src_dir)
    
    def copy_additional_patch(self, ctxt):
        # 复制centos/patches/* 到 rpmbuild/SOURCES
        ctxt.patch_dir = os.path.join(ctxt.distro_dir, "patches")
        if not os.path.exists(ctxt.patch_dir):
            log.info("patches not found in %s" % ctxt.pkgdir)
            return
        log.info('copy additional patches from DIR: %s' % ctxt.patch_dir)
        utils.copy(ctxt.patch_dir, ctxt.build_src_dir)

    def compile(self, ctxt):
        rpm.install_build_dependence(ctxt.srpmfiles[0])
        rpm.build_rpm(ctxt, self.ctxt.platform_release)

    def copy_to_output(self, ctxt):
        ctxt.rpmfiles = utils.find_out_files(ctxt.build_rpm_dir, ".rpm")
        for rpmfile in ctxt.rpmfiles + ctxt.srpmfiles:
            utils.copy(rpmfile, self.ctxt.output)

    def apply_meta_patches(self, ctxt):
        ctxt.meta_patch_dir = os.path.join(ctxt.distro_dir, "meta_patches")
        if not os.path.exists(ctxt.meta_patch_dir):
            log.info("no meta patches")
            return
        log.info('apply meta patches. DIR: %s' % ctxt.meta_patch_dir)
        ctxt.meta_patch_order = os.path.join(ctxt.meta_patch_dir, "PATCH_ORDER")
        log.info("PATCH ORDER: %s" % ctxt.meta_patch_order)
        for line in open(ctxt.meta_patch_order):
            patchfile = os.path.join(ctxt.meta_patch_dir, line.strip())
            shell.patch_apply(ctxt, patchfile)