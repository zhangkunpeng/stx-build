import os,shutil
import process, log

patch="/usr/bin/patch"
git="/usr/bin/git"

def patch_apply(ctxt, patchfile):
    if not os.path.isfile(patchfile):
        return
    log.info("apply patch: %s" % patchfile)
    #patch -f $PATCH_ARGS --no-backup-if-mismatch < $PATCH
    #cmd = [patch, '-f', '-p1', '--no-backup-if-mismatch', '<', patchfile]
    cmd = ["%s -f -p1 --no-backup-if-mismatch < %s" %(patch, patchfile)]
    process.check_call(cmd, cwd=ctxt.build_dir, shell=True)

def echo_env(ctxt, KEY):
    cmd = ["source %s && echo $%s" % (ctxt.build_srpm_data ,KEY)]
    return process.check_output(cmd, env=ctxt, shell=True)

def git_checkout(context):
    context.distdir = os.path.join(context.rootdir, "source")
    log.info("fetch repo: %s, branch: %s, distdir: %s" % (context.source, context.branch, context.distdir))
    if os.path.exists(context.distdir) and context.source != context.distdir:
        shutil.rmtree(context.distdir)
    if os.path.isdir(context.source):
        shutil.copy(context.source, context.distdir)
    elif context.source.startswith("http"):
        process.check_call(["git","clone",context.source,"--depth=1", "--branch=%s" % context.branch, context.distdir])
    else:
        log.error("Cannot get repo")

def git_commit_count(repodir, commit_id):
    cmd = [git, "rev-list", "--count", "%s..HEAD" % commit_id]
    output = process.check_output(cmd, cwd=repodir)
    return int(output)

def git_plus_by_status(repodir):
    cmd = [git, "status", "--porcelain"]
    output = process.check_output(cmd, cwd=repodir)
    return 1 if output else 0