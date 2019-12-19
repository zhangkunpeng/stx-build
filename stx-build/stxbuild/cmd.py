import sys,os
from common.repo import RepoManager
from common.build import BuildManager,Build

import argparse
from common import log

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="input the git repo which to build")
    parser.add_argument("--branch", help="the git repo branch", default="master")
    parser.add_argument("--type", help="build type", choices=["std", "rt"], default="std")
    parser.add_argument("--workdir", help="input the work dir", default=os.getcwd())
    parser.add_argument("--srcdir", help="input the src dir", default=os.getcwd())
    args = parser.parse_args()
    if not args.repo:
        print("Please input the git repo which to build")
        print("=================================")
        parser.print_help()
        exit(1)
    if not os.path.exists(args.workdir):
        os.makedirs(args.workdir)
    if not os.path.exists(args.srcdir):
        os.makedirs(args.srcdir)
    repo = args.repo.rstrip('/')
    repo_name = os.path.splitext(os.path.basename(repo))[0]
    src_path = os.path.join(args.srcdir, repo_name)
    work_path = os.path.join(args.workdir, "build", args.type, repo_name)
    log.CONF(filename=os.path.join(args.workdir,"logs", "%s.log" % repo_name), 
             name=repo_name)
    
    git_repo = RepoManager(repo, path=src_path)
    git_repo.checkout(branch=args.branch)
    build_mgr = BuildManager(work_path, src_path, args.type)
    build_mgr.build_pkgs()

if __name__ == '__main__':
    sys.exit(main())
