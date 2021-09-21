from io import DEFAULT_BUFFER_SIZE
from models.ImageCollectionPPMModel import ImageCollectionPPMModel
from models.ImageCollectionVideoModel import ImageCollectionVideoModel
from models.ImageCollectionFolderModel import ImageCollectionFolderModel
import os
from getpass import getpass
from PyQt5 import QtCore
from pexpect.exceptions import TIMEOUT, EOF
from models.ImageCollectionModel import ImageCollectionModel

class ImageCollectionCloudModel(ImageCollectionModel):
    DEFAULT_LOCAL_ROOT_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'tmp'))

    def __init__(self, path, name, type, localPath=None, parentModel=None):
        super().__init__()
        self.path = path
        self.name = name
        self.type = type
        assert self.type in ('folder', 'video', 'ppm')
        self.parentModel = parentModel

        if localPath is None:
            self.localPath = os.path.join(ImageCollectionCloudModel.DEFAULT_LOCAL_ROOT_PATH, name)
        else:
            self.localPath = localPath
        self.localPath = os.path.normpath(self.localPath)

        self.serverAddr = self.path.split(':')[0]
        
        flag = self.load(self.path, self.localPath)
        if flag == False:
            raise RuntimeError('Unable to load the image collection from the server.')
        
        self.model = self.getModel()


    def load(self, serverPath, localPath):
        import pexpect
        if self.type == 'folder' and not serverPath.endswith('/'):
            serverPath = serverPath + '/'

        cmd = f'rsync -a --delete {serverPath} {localPath}'      #rsync -av --delete xxx@gypsum.cs.umass.edu:~/testData /Users/xxx/Desktop/tmp
        child = pexpect.spawn(cmd)
        
        i = child.expect(["password", EOF, TIMEOUT], timeout=30)
        # print(i, child.before, child.after)
        if i != 0:
            print('Unexpected situation')
            return False

        passwd = getpass()
        child.sendline(passwd)
        i = child.expect(["Permission denied", 'failed', 'error', EOF, TIMEOUT], timeout=200)
        # print(i, child.before, child.after)
        if i == 0:
            print('Permission denied')
            return False
        elif i == 3:
            print('Ok')
            return True
        elif i == 4:
            print('Timeout')
            return False
        else:
            print('Error')
            return False

        # import paramiko
        # trans = paramiko.Transport(('gypsum.cs.umass.edu', 22))
        # trans.connect(username='zhipengtang', password=getpass())
        # sftp = paramiko.SFTPClient.from_transport(trans)
        # localpath = '/Users/zhipengtang/Desktop/tmp'
        # remotepath = '~/testData'

        # sftp.get(remotepath, localpath)
        # trans.close()


    def getModel(self):
        modelClassDict = {'folder': ImageCollectionFolderModel, 'video': ImageCollectionVideoModel,'ppm': ImageCollectionPPMModel}
        modelClass = modelClassDict[self.type]
        model = modelClass(self.localPath, self.name, parentModel=self.parentModel)
        return model
        
    def length(self):
        return self.model.length()
    
    def getImg(self, idx):
        return self.model.getImg(idx)
    
    def getImgName(self, idx):
        return self.model.getImgName(idx)

    def getRootPath(self):
        return self.path

    def getImgInfo(self, idx):
        rootPath = self.getRootPath()
        idx = idx

        if self.type == 'folder':
            imgFileName = os.path.split(self.model.getImgInfo(idx)['path'])[1]
            path = os.path.join(rootPath, imgFileName)
        elif self.type == 'video' or self.type == 'ppm':
            path = rootPath + f':{idx}'
        
        return {'idx': idx, 'path': path, 'rootPath': rootPath}


if __name__ == '__main__':
    model = ImageCollectionCloudModel('zhipengtang@gypsum.cs.umass.edu:~/testData/batch_00002_0', 'testData')
    