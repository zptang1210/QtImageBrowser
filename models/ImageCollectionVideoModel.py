import os, sys
from models.ImageCollectionBasicModel import ImageCollectionBasicModel
from utils.pathUtils import normalizePath

if sys.platform == 'darwin' or sys.platform == 'win32':

    import cv2
    from decord import VideoReader
    from decord import cpu

    class ImageCollectionVideoModel(ImageCollectionBasicModel):
        def __init__(self, path, name, parentModel=None):
            super().__init__()
            assert path == normalizePath(path)
            self.path = path
            self.name = name
            self.parentModel = parentModel
            self.sourceModel = self
            self.sourceModelTypeName = 'video'

            try:
                self.vr = VideoReader(self.path, ctx=cpu(0))
            except:
                raise RuntimeError('Unable to load the video file.')

        def length(self):
            return len(self.vr)

        def getImg(self, idx):
            assert idx >= 0 and idx < self.length()
            frame = self.vr[idx].asnumpy()
            return frame

        def getImgName(self, idx):
            assert idx >= 0 and idx < self.length()
            return 'frame_' + ('%06d' % idx)

        def getRootPath(self):
            return normalizePath(os.path.dirname(self.path))

        def getImgInfo(self, idx):
            path = self.path + f':{idx}'
            rootPath = self.getRootPath()
            idx = idx
            return {'idx': idx, 'path': path, 'rootPath': rootPath}

        @staticmethod
        def saveModel(modelToSave, savePath, fps=30):
            if os.path.exists(savePath): return False

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            img_size = modelToSave.getImg(0).shape
            size = img_size[:2]
            out = cv2.VideoWriter(savePath, fourcc, fps, (size[1], size[0]))
            try:
                for idx in range(modelToSave.length()):
                    img_np = modelToSave.getImg(idx)
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                    out.write(img_np)
            except:
                return False
            finally:
                out.release()
                
            return True

elif sys.platform.startswith('linux'):

    import cv2
    os.environ.pop("QT_QPA_PLATFORM_PLUGIN_PATH") # https://stackoverflow.com/questions/63829991/qt-qpa-plugin-could-not-load-the-qt-platform-plugin-xcb-in-even-though-it

    class ImageCollectionVideoModel(ImageCollectionBasicModel):
        def __init__(self, path, name, parentModel=None):
            super().__init__()
            assert path == normalizePath(path)
            self.path = path
            self.name = name
            self.parentModel = parentModel

            # open the video
            self.cap = cv2.VideoCapture(self.path)
            if not self.cap.isOpened():
                self.cap = None
                raise RuntimeError('Unable to load the video file.')

            # get frame #
            self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # bring all frames to the memory
            self.frames = []
            while(self.cap.isOpened()):
                ret, frame = self.cap.read()
                if ret == True:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    self.frames.append(frame_rgb)
                else:
                    break

        def __del__(self):
            if self.cap is not None:
                self.cap.release()
                self.cap = None

        def length(self):
            return self.frame_count

        def getImg(self, idx):
            assert idx >= 0 and idx < self.length()
            frame = self.frames[idx]
            return frame

        def getImgName(self, idx):
            assert idx >= 0 and idx < self.length()
            return 'frame_' + ('%06d' % idx)

        def getRootPath(self):
            return normalizePath(os.path.dirname(self.path))

        def getImgInfo(self, idx):
            path = self.path + f':{idx}'
            rootPath = self.getRootPath()
            idx = idx
            return {'idx': idx, 'path': path, 'rootPath': rootPath}

        @staticmethod
        def saveModel(modelToSave, savePath, fps=30):
            if os.path.exists(savePath): return False

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            img_size = modelToSave.getImg(0).shape
            size = img_size[:2]
            out = cv2.VideoWriter(savePath, fourcc, fps, (size[1], size[0]))
            try:
                for idx in range(modelToSave.length()):
                    img_np = modelToSave.getImg(idx)
                    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                    out.write(img_np)
            except:
                return False
            finally:
                out.release()
                
            return True
