from stxbuild.common import process
import os, re, subprocess
rpm = "/usr/bin/rpm"
rpmbuild = "/usr/bin/rpmbuild"
yumbuilddep = "/usr/bin/yum-builddep"
createrepo = "/usr/bin/createrepo"
yum = "/usr/bin/yum"
yumconf = "/etc/local.yum.conf"

def query_srpm_name(srpmfile):
    cmd = [rpm,"-qp", "--queryformat=%{NAME}","--nosignature", srpmfile]
    return process.check_output(cmd).strip()

def query_srpm_version(srpmfile):
    cmd = [rpm,"-qp", "--queryformat=%{VERSION}","--nosignature", srpmfile]
    return process.check_output(cmd).strip()

def query_srpm_release(srpmfile):
    cmd = [rpm,"-qp", "--queryformat=%{RELEASE}","--nosignature", srpmfile]
    return process.check_output(cmd).strip()

def srpm_extract(ctxt):
    # rpm -i --nosignature --root=$ROOT_DIR --define="%_topdir $BUILD_DIR" $ORIG_SRPM_PATH 2>> /dev/null
    cmd = [rpm, "-i", "--nosignature", "--define", "%%_topdir %s" % ctxt.build_dir, ctxt.orig_srpm_path]
    process.check_call(cmd, stderr=-2)

def query_spec_release(ctxt, specfile):
    release = None
    for line in open(specfile):
        r = re.search(r'^Release: (.*)', line.strip())
        if r :
            release = r.group(1)
    if release:
        release = release.replace("%{{tis_patch_ver}}", ctxt.TIS_PATCH_VER)\
                         .replace("%{{?_tis_dist}}", ctxt.TIS_DIST)\
                         .replace("%{{_tis_dist}}", ctxt.TIS_DIST)
    return release

def build_srpm(ctxt, platform_release, build_type):
    # sed -i -e "1 i%define _tis_build_type $BUILD_TYPE" $SPEC_PATH
    # sed -i -e "1 i%define tis_patch_ver $TIS_PATCH_VER" $SPEC_PATH
    lines = []
    with open(ctxt.specfile, 'r') as f:
        for l in f:
            lines.append(l)
    lines.insert(0, "%%define _tis_build_type %s\n" % build_type)
    lines.insert(0, "%%define tis_patch_ver %s\n" % ctxt.TIS_PATCH_VER)
    with open(ctxt.specfile, 'w') as f:
        f.write(''.join(lines))
    cmd = [rpmbuild,"-bs",ctxt.specfile, 
                    "--undefine=dist", 
                    "--define=platform_release %s" % platform_release,
                    "--define=%%_topdir %s" % ctxt.build_dir,
                    "--define=_tis_dist %s" % ctxt.TIS_DIST]
    process.check_call(cmd)

def build_rpm(ctxt, platform_release):
    cmd = [rpmbuild,"--rebuild", ctxt.srpmfile, 
                    "--define=platform_release %s" % platform_release,
                    "--define=%%_topdir %s" % ctxt.build_dir,
                    "--define=_tis_dist %s" % ctxt.TIS_DIST]
    process.check_call(cmd)

def install_build_dependence(srpmfile):
    cmd = [yumbuilddep, "-c", yumconf, srpmfile]
    process.check_call(cmd)

def install_rpm(rpmfile):
    cmd = [yumbuilddep, "-c", yumconf, rpmfile]
    process.check_call(cmd)

def update_repodata(repopath):
    cmd = [createrepo,"-c", yumconf, "--update", repopath]
    process.check_call(cmd)

def yum_clean_cache():
    cmd = [yum,"-c", yumconf, "clean", "all"]
    process.check_call(cmd)

def yum_makecache():
    cmd = [yum,"-c", yumconf, "makecache"]
    process.check_call(cmd)