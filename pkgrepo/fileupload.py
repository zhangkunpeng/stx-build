import tornado.ioloop
import tornado.web
import shutil
import os
import json
import subprocess

root="/tmp"

class FileUploadHandler(tornado.web.RequestHandler):

    def get(self):
        self.write(''' <html> <head><title>Upload File</title></head> <body> <form action='file' enctype="multipart/form-data" method='post'> <input type='file' name='file'/><br/> <input type='submit' value='submit'/> </form> </body> </html> ''')

    def post(self):
        ret = {'result': 'OK'}
        upload_path = self.repo_path()  # 文件的暂存路径
        file_metas = self.request.files.get('file', None)  # 提取表单中‘name’为‘file’的文件元数据

        if not file_metas:
            ret['result'] = 'Invalid Args'
            return ret

        for meta in file_metas:
            filename = meta['filename']
            file_path = os.path.join(upload_path, filename)

            with open(file_path, 'wb') as up:
                up.write(meta['body'])
                # OR do other thing

        self.write(json.dumps(ret))
    
    def repo_path(self):
        return os.path.join(root, "tmp")
    
    

class RpmUploadHandler(FileUploadHandler):

    def get(self):
        retcode = self.update_repodata()
        if retcode:
            self.write("failed")
        else:
            self.write("success")

    def update_repodata(self):
        if not os.path.exist(self.repo_path()):
            os.makedirs(self.repo_path())
        command = ["/usr/bin/createrepo","--update",self.repo_path()]
        return subprocess.call(command)

    def repo_path(self):
        return os.path.join(root, "centos/rpm")

class DebUploadHandler(FileUploadHandler):

    def get(self):
        retcode = self.update_repodata()
        if retcode:
            self.write("failed")
        else:
            self.write("success")

    def update_repodata(self):
        return 0

    def repo_path(self):
        return os.path.join(root, "debian/deb")