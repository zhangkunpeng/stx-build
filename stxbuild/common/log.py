import logging,os, time
import logging.handlers

logger = None

def CONF(context):
    filename = "%s.log" % time.strftime("%y%m%d-%H%M%S", time.localtime())
    filename = os.path.join(context.rootdir, "logs", filename)
    context.logfile = filename
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    global logger
    logger = logging.getLogger(context.reponame)
    handler1 = logging.StreamHandler()
    handler2 = logging.FileHandler(filename=filename)

    logger.setLevel(logging.DEBUG)
    handler1.setLevel(logging.DEBUG)
    handler2.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    handler1.setFormatter(formatter)
    handler2.setFormatter(formatter)

    logger.addHandler(handler1)
    logger.addHandler(handler2)

def info(msg):
    if not logger:
        print("please config logger")
        exit(1)
    logger.info(msg)

def debug(msg):
    logger.debug(msg)

def warning(msg):
    logger.warning(msg)

def error(msg):
    logger.error(msg)
    exit(1)

def critical(msg):
    logger.critical(msg)
    exit(1)
