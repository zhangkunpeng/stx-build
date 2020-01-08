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
            if "stdout"in kw: kw.pop("stdout")
            with open(kw.get("stdoutfile"), 'a') as f:
                f.writelines(["", dividing_line, cmd, dividing_line])
                f.flush
        result = func(*args, **kw)
        log.info("Execute result: %s" % result)
        return result
    return wrapper

@logprocess
def check_call(*popenargs, **kwargs):
    if kwargs.get("stdoutfile"):
        with open(kwargs.get("stdoutfile"), "a") as f:
            kwargs.pop("stdoutfile")
            return subprocess.check_call(*popenargs, stdout=f, **kwargs)
    return subprocess.check_call(*popenargs, **kwargs)

@logprocess
def check_output(*popenargs, **kwargs):
    return subprocess.check_output(*popenargs, **kwargs).strip()

def call(*popenargs, **kwargs):
    log.info(json.dumps(popenargs))
    subprocess.call(*popenargs,**kwargs)

