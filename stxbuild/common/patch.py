import process, log
import os, shutil
patch="/usr/bin/patch"

def patch_apply(ctxt, patchfile):
    log.info("apply patch: %s" % patchfile)
    #patch -f $PATCH_ARGS --no-backup-if-mismatch < $PATCH
    cmd = [patch, '-f', '-p1', '--no-backup-if-mismatch', '<', patchfile]
    process.check_call(cmd, cwd=ctxt.build_dir)

def apply_meta_patches(ctxt):
    ctxt.meta_patch_dir = os.path.join(ctxt.distro_dir, "meta_patches")
    log.info('apply meta patches. DIR: %s' % ctxt.meta_patch_dir)
    ctxt.meta_patch_order = os.path.join(ctxt.meta_patch_dir, "PATCH_ORDER")
    log.info("PATCH ORDER: %s" % ctxt.meta_patch_order)
    for line in open(ctxt.meta_patch_order):
        patchfile = os.path.join(ctxt.meta_patch_dir, line.strip())
        patch_apply(ctxt, patchfile)

def add_other_patches(ctxt):
    patch_dir = os.path.join(ctxt.distro_dir, "patches")
    if not os.path.exists(patch_dir):
        log.info("patches not found in %s" % ctxt.pkgdir)
        return
    log.info('add other patches. DIR: %s' % patch_dir)
    ctxt.patch_dir = patch_dir
    for patch in os.listdir(ctxt.patch_dir):
        patchfile = os.path.join(ctxt.patch_dir, patch)
        copyto = os.path.join(ctxt.build_dir, "SOURCES", patch)
        log.info("copy patch from '%s' to '%s'" % (patchfile, copyto))
        shutil.copy2(patchfile, copyto)

def add_other_files(ctxt):
    # 逻辑有问题，需要修复
    files_dir = os.path.join(ctxt.pkgdir, "files")
    if not os.path.exists(files_dir):
        log.info("patches not found in %s" % ctxt.pkgdir)
        return
    log.info('add other files. DIR: %s' % files_dir)
    ctxt.files_dir = files_dir
    for filename in os.listdir(files_dir):
        copyfile = os.path.join(files_dir, filename)
        copyto = os.path.join(ctxt.build_dir, "SOURCES", filename)
        log.info("copy patch from '%s' to '%s'" % (copyfile, copyto))
        shutil.copy2(copyfile, copyto)