
from common import args, log
from common import git
from common.context import Context
from common.build import Build
import json


def main():
    context = Context()
    args.prepare_context(context)
    log.CONF(context)

    log.debug(json.dumps(context))
    log.info("Start to build repo %s" % context.reponame)

    git.checkout(context)

    build = Build(context)
    build.build()

if __name__ == '__main__':
    sys.exit(main())

