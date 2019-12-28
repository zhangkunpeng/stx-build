import process


def echo_env(ctxt, KEY):
    cmd = ["source %s && echo $%s" % (ctxt.build_srpm_data ,KEY)]
    process.check_output(cmd, env=ctxt, shell=True)