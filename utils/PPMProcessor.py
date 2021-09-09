import math
import numpy as np
from PIL import Image

def writeSuperPPM(imgList, savePath, numPerRow=10):
    '''Write a set of images of the same size into a super PPM file.

    Args:
        imgList: a list of images in numpy uint8 format. These images should be of the same size. The shape of each image is [H, W, C] where C is for RGB
        savePath: the path to save the generated super PPM file
        numPerRow: the number of images saved in each row

    Returns:
        True if the function runs correctly. Otherwise, False
    '''
    imgHeight, imgWidth, imgCh = imgList[0].shape
    imgNum = len(imgList)
    with open(savePath, 'w') as fout:
        fout.write('P6\n')
        fout.write(f'# {imgHeight} {imgWidth} {imgCh} {imgNum} {numPerRow}\n')

        totalRows = math.ceil(imgNum / numPerRow)
        sPPMHeight = totalRows * imgHeight
        sPPMWidth = numPerRow * imgWidth

        fout.write(f'{sPPMWidth} {sPPMHeight}\n')
        fout.write('255\n')
    
    with open(savePath, 'ab') as fout:
        sPPMNumpy = np.zeros((sPPMHeight, sPPMWidth * 3), np.uint8)

        for i, img in enumerate(imgList):
            assert img.shape == (imgHeight, imgWidth, imgCh)
            assert img.dtype == np.uint8

            img_ = img.reshape((imgHeight, imgWidth * imgCh))

            sPPMRowIdx = i // numPerRow # the index of the tile where the given image should put
            sPPMColIdx = i % numPerRow
            sPPMNumpy[sPPMRowIdx * imgHeight : (sPPMRowIdx+1) * imgHeight, sPPMColIdx * imgWidth * 3 : (sPPMColIdx+1) * imgWidth  * 3] = img_
        
        sPPMNumpy.tofile(fout)


def readSuperPPM(filePath):
    '''Read a super PPM file and return back a list of images

    Args:
        filePath: the path of the super PPM file
    
    Returns:
        a list of images in numpy uint8 format. These images should be of the same size. The shape of each image is [H, W, C] where C is for RGB
    '''
    img = Image.open(filePath)
    img = np.asarray(img)
    
    with open(filePath, 'r', encoding='ascii', errors='ignore') as fin:
        ppmFormat = fin.readline()
        assert ppmFormat.strip() == 'P6'

        metadata_raw = fin.readline().strip()
        metadata_str = metadata_raw.split(' ')[1:]
        metadata = tuple(map(int, metadata_str))
        # print(metadata)
    
    height, width, ch, num, numPerRow = metadata
    # print(img.shape)

    imgList = []
    for i in range(num):
        sPPMRowIdx = i // numPerRow
        sPPMColIdx = i % numPerRow
        # print(sPPMRowIdx, sPPMColIdx)

        subImg = img[sPPMRowIdx * height : (sPPMRowIdx+1) * height, sPPMColIdx * width : (sPPMColIdx+1) * width, :]
        # print(subImg.shape)
        imgList.append(subImg)
    
        # print(len(imgList))

    return imgList


if __name__ == '__main__':
    # OpenCV version
    # import cv2
    # dogImg = cv2.imread('dog.jpeg')
    # dogImg = cv2.cvtColor(dogImg, cv2.COLOR_BGR2RGB)

    # PIL version
    rawImg = Image.open('mnist.jpg')
    rawImg = rawImg.convert('RGB')
    rawImg = np.asarray(rawImg)

    writeSuperPPM([rawImg]*100, 'mnist.ppm', numPerRow=8)
    imgList = readSuperPPM('mnist.ppm')
    for img in imgList:
        img_pil = Image.fromarray(img)
        # img_pil.show()