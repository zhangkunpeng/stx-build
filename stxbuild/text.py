
# class Text(object):

#     def __new__(cls, *args, **kwargs):
#         return object.__new__(AText) 

#     def __init__(self):
#         pass

#     def print(self):
#         print("Text")

# class AText(Text):

#     def __init__(self):
#         pass

#     def print(self):
#         print("AText")

# txt = Text()
# txt.print()
# print(txt.__class__.__name__)

# import subprocess 
# git="/usr/bin/git"
# count = 0
# git_cmd = [git, "rev-list", "--count", "44eab48884..HEAD"]
# print(subprocess.check_output(git_cmd,cwd="../../stx-pipeline/centos"))
# count = count + int(subprocess.check_output(git_cmd,cwd="../../stx-pipeline/centos"))
# git_cmd = [git, "status", "--porcelain"]
# print(subprocess.check_output(git_cmd, cwd="../../stx-pipeline/centos"))
# count = count + int(subprocess.check_output(git_cmd))
# from common.context import Context
# ctxt = Context(a="b")
# print(ctxt.a)
# print(ctxt["a"])
# print(ctxt.b)
# print(ctxt["c"])
def test(a="1", *args, **kw):
    print(a, args, kw)

def test2(*args, **kw):
    test(*args, **kw)

test2(a="2")