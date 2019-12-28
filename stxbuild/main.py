
from common import args, log
from common import shell
from common.context import Context
from common.build import Build
import json,sys


def main():
    context = Context()
    args.prepare_context(context)
    log.CONF(context)

    log.debug(json.dumps(context))
    log.info("Start to build repo %s" % context.reponame)

    shell.git_checkout(context)

    build = Build(context)
    build.build()

if __name__ == '__main__':
    sys.exit(main())

