import log
import json
import subprocess

def check_call(*popenargs, **kwargs):
    log.info(json.dumps(popenargs))
    subprocess.check_call(*popenargs,**kwargs)

def check_output(*popenargs, **kwargs):
    log.info(json.dumps(popenargs))
    output = subprocess.check_output(*popenargs, **kwargs).strip()
    log.info("output: %s" % output)
    return output