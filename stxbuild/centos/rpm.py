from stxbuild.common import process, log
import os, re, subprocess
rpm = "/usr/bin/rpm"
rpmbuild = "/usr/bin/rpmbuild"
rpmspec = "/usr/bin/rpmspec"
yumbuilddep = "/usr/bin/yum-builddep"
createrepo = "/usr/bin/createrepo"
yum = "/usr/bin/yum"
yumconf = "/etc/yum.conf"

def rpmlogfile(ctxt):
    return os.path.join(ctxt.workdir, "build.log")

def query_srpm_tag(srpmfile, tag):
    cmd = [rpm,"-qp", "--queryformat=%%{%s}" % tag.upper(), "--nosignature", srpmfile]
    return process.check_output(cmd).strip()

def srpm_extract(ctxt):
    # rpm -i --nosignature --root=$ROOT_DIR --define="%_topdir $BUILD_DIR" $ORIG_SRPM_PATH 2>> /dev/null
    cmd = [rpm, "-i", "--nosignature", "--define=%%_topdir %s" % ctxt.build_dir, ctxt.orig_srpm_path]
    process.check_call(cmd, stdoutfile=rpmlogfile(ctxt))

def query_spec_tag(specfile, tag):
    for line in open(specfile):
        r = re.search('^%s:(.*)' % tag.capitalize(), line.strip())
        if r :
            out = r.group(1)
            if out:
                return out.strip()
    log.error("query spec tag: %s in %s failed" % (tag, specfile))
    

def build_tmp_spec(ctxt, platform_release, build_type):
    cmd = [rpmspec, "-P", ctxt.orig_spec_path,
                    "--define=platform_release %s" % platform_release,
                    "--define=%%_topdir %s" % "/tmp",
                    "--define=_tis_dist %s" % ctxt.TIS_DIST,
                    "--define=tis_patch_ver %s" % ctxt.TIS_PATCH_VER,
                    "--define=_tis_build_type %s" % build_type]
    ctxt.tmpspec = os.path.join(ctxt.rootdir, "tmpspec", "tmp_"+os.path.basename(ctxt.orig_spec_path))
    process.check_call(cmd, stdoutfile=ctxt.tmpspec)

def build_srpm(ctxt, platform_release, build_type):
    # sed -i -e "1 i%define _tis_build_type $BUILD_TYPE" $SPEC_PATH
    # sed -i -e "1 i%define tis_patch_ver $TIS_PATCH_VER" $SPEC_PATH
    lines = []
    with open(ctxt.specfiles[0], 'r') as f:
        for l in f:
            lines.append(l)
    lines.insert(0, "%%define _tis_build_type %s\n" % build_type)
    lines.insert(0, "%%define tis_patch_ver %s\n" % ctxt.TIS_PATCH_VER)
    with open(ctxt.specfiles[0], 'w') as f:
        f.write(''.join(lines))
    cmd = [rpmbuild,"-bs",ctxt.specfiles[0], 
                    "--undefine=dist", 
                    "--define=platform_release %s" % platform_release,
                    "--define=%%_topdir %s" % ctxt.build_dir,
                    "--define=_tis_dist %s" % ctxt.TIS_DIST]
    process.check_call(cmd)

def build_rpm(ctxt, platform_release):
    cmd = [rpmbuild,"--rebuild", ctxt.srpmfiles[0], 
                    "--define=platform_release %s" % platform_release,
                    "--define=%%_topdir %s" % ctxt.build_dir,
                    "--define=_tis_dist %s" % ctxt.TIS_DIST]
    result = process.check_call(cmd, stdoutfile=rpmlogfile(ctxt))
    if result == 0:
        log.info("^^^^^ %s BUILD SUCCESS" % ctxt.fullname)

def install_build_dependence(srpmfile):
    cmd = [yumbuilddep, "-c", yumconf, "-y", srpmfile]
    process.check_call(cmd)

def install_rpm(rpmfile):
    cmd = [yumbuilddep, "-c", yumconf, "-y", rpmfile]
    process.check_call(cmd)

def update_repodata(repopath):
    cmd = [createrepo, "--update", repopath]
    process.check_call(cmd)

def yum_clean_cache():
    cmd = [yum,"-c", yumconf, "clean", "all"]
    process.check_call(cmd)

def yum_makecache():
    cmd = [yum,"-c", yumconf, "makecache"]
    process.check_call(cmd)

def yum_install(package):
    cmd = [yum,"-c", yumconf, "install", "-y", package]
    process.check_call(cmd)