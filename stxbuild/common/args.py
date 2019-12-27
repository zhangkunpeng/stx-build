import argparse
import os
from context import Context

def prepare_context(context):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", help="input the source which to build")
    parser.add_argument("--branch", help="the git repo branch")
    parser.add_argument("--type", help="build type", choices=["std", "rt"], default="std")
    parser.add_argument("--rootdir", help="input the work dir")
    args = parser.parse_args()
    if not args.source:
        print("Please input the git repo which to build")
        print("=================================")
        parser.print_help()
        exit(1)
    context.source = args.source
    context.branch = args.branch if args.branch else os.environ.get("BRANCH", "master")
    context.build_type = args.type
    context.rootdir = args.rootdir if args.rootdir else os.environ.get("ROOTDIR", os.getcwd())
    context.reponame = os.path.splitext(os.path.basename(args.source))[0]
    context.mirror = os.environ.get("MIRROR", os.path.join(os.path.dirname(context.rootdir), "mirror"))
    context.workdir = os.path.abspath(os.path.join(context.rootdir, args.type))
    context.TIS_DIST = ".tis"
    