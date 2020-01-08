import log
import json
import subprocess

def logprocess(func):
    def wrapper(*args, **kw):
        cmd = " ".join(args[0])
        dividing_line = "".ljust(len(cmd), "*")
        log.info("")
        log.info(dividing_line)
        log.info(cmd)
        log.info(dividing_line)
        if kw.get("stdoutfile"):
            with open(kw.get("stdoutfile"), 'a') as f:
                f.writelines(["\n", dividing_line,"\n", cmd, "\n\n"])
                f.flush()
        result = func(*args, **kw)
        log.info("Execute result: %s" % result)
        return result
    return wrapper

@logprocess
def check_call(*popenargs, **kwargs):
    if kwargs.get("stdoutfile"):
        with open(kwargs.get("stdoutfile"), "a") as f:
            kwargs.pop("stdoutfile")
            if "stdout" not in kwargs:
                kwargs["stdout"] = f
            if "stderr" not in kwargs:
                kwargs["stderr"] = f
            return subprocess.check_call(*popenargs, **kwargs)
    return subprocess.check_call(*popenargs, **kwargs)

@logprocess
def check_output(*popenargs, **kwargs):
    return subprocess.check_output(*popenargs, **kwargs).strip()

def call(*popenargs, **kwargs):
    log.info(json.dumps(popenargs))
    subprocess.call(*popenargs,**kwargs)

