
import tornado
import fileupload
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="input the root path", default="/tmp")
    args = parser.parse_args()
    fileupload.root = args.root
    app = tornado.web.Application([
        (r'/rpm', fileupload.RpmUploadHandler),
        (r'/deb', fileupload.DebUploadHandler),
    ])
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()