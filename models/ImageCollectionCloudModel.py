from io import DEFAULT_BUFFER_SIZE
from models.ImageCollectionPPMModel import ImageCollectionPPMModel
from models.ImageCollectionVideoModel import ImageCollectionVideoModel
from models.ImageCollectionFolderModel import ImageCollectionFolderModel
import os
from getpass import getpass
from PyQt5 import QtCore
from pexpect.exceptions import TIMEOUT, EOF
from models.ImageCollectionModel import ImageCollectionModel
import utils.PasswdManager as PasswdManager
import pexpect

class ImageCollectionCloudModel(ImageCollectionModel):
    DEFAULT_LOCAL_ROOT_PATH = os.path.normpath(os.path.join('.', 'tmp'))

    def __init__(self, path, name, type, localPath=None, preload=True, parentModel=None):
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
        
        if preload:
            flag = self.load(self.path, self.localPath)
            self.loaded = True
            if flag == False:
                raise RuntimeError('Unable to load the image collection from the server.')
        
            self.model = self.getModel()
        else:
            self.loaded = False
            self.model = None


    def load(self, serverPath, localPath):
        if self.type == 'folder' and not serverPath.endswith('/'):
            serverPath = serverPath + '/'

        cmd = f'rsync -a --delete {serverPath} {localPath}'      #rsync -av --delete xxx@gypsum.cs.umass.edu:~/testData /Users/xxx/Desktop/tmp
        print('rsync cmd: ', cmd)
        child = pexpect.spawn(cmd)
        
        i = child.expect(["password", EOF, TIMEOUT], timeout=30)
        # print(i, child.before, child.after)
        if i != 0:
            print('Unexpected situation')
            return False

        passwd = PasswdManager.passwdManager.getPass()
        child.sendline(passwd)
        i = child.expect(["Permission denied", 'failed', 'error', EOF, TIMEOUT], timeout=200)
        # print(i, child.before, child.after)
        if i == 0:
            print('rsync Permission denied')
            PasswdManager.passwdManager.currentPasswdIsInvalid()
            self.loaded = False
            return False
        elif i == 3:
            print('rsync Ok')
            self.loaded = True
            return True
        elif i == 4:
            print('rsync Timeout')
            self.loaded = False
            return False
        else:
            print('rsync Error')
            self.loaded = False
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
        assert self.loaded
        return self.model.length()
    
    def getImg(self, idx):
        assert self.loaded
        return self.model.getImg(idx)
    
    def getImgName(self, idx):
        assert self.loaded
        return self.model.getImgName(idx)

    def getRootPath(self):
        return self.path

    def getImgInfo(self, idx):
        assert self.loaded
        rootPath = self.getRootPath()
        idx = idx

        if self.type == 'folder':
            imgFileName = os.path.split(self.model.getImgInfo(idx)['path'])[1]
            path = os.path.join(rootPath, imgFileName)
        elif self.type == 'video' or self.type == 'ppm':
            path = rootPath + f':{idx}'
        
        return {'idx': idx, 'path': path, 'rootPath': rootPath}

    @staticmethod
    def saveModel(modelToSave, savePath):
        raise NotImplemented()


if __name__ == '__main__':
    model = ImageCollectionCloudModel('zhipengtang@gypsum.cs.umass.edu:~/testData/batch_00002_0', 'testData')
    