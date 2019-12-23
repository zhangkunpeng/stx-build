import tornado.ioloop
import tornado.web
import shutil
import os
import json


class FileUploadHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(''' <html> <head><title>Upload File</title></head> <body> <form action='file' enctype="multipart/form-data" method='post'> <input type='file' name='file'/><br/> <input type='submit' value='submit'/> </form> </body> </html> ''')

    def post(self):
        ret = {'result': 'OK'}
        upload_path = os.path.join(os.path.dirname(__file__), 'files')  # 文件的暂存路径
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


app = tornado.web.Application([
    (r'/file', FileUploadHandler),
])

if __name__ == '__main__':
    app.listen(8080)
    tornado.ioloop.IOLoop.instance().start()