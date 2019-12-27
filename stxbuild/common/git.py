import os,shutil
import log
import process

git="/usr/bin/git"
def checkout(context):
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

def commit_count(ctxt):
    cmd = [git, "rev-list", "--count", "%s..HEAD" % ctxt.TIS_BASE_SRCREV]
    output = process.check_output(cmd, cwd=ctxt.pkgdir)
    return int(output)

def plus_by_status(ctxt):
    cmd = [git, "status", "--porcelain"]
    output = process.check_output(cmd, cwd=ctxt.pkgdir)
    return 1 if output else 0
