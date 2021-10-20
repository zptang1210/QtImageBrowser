import sys
import cv2

if __name__ == '__main__':
    imgPath = sys.argv[1]
    outputPath = sys.argv[2]
    print(imgPath)
    print(outputPath)

    img = cv2.imread(imgPath)
    bbox = cv2.selectROI(img, False)

    if bbox == (0, 0, 0, 0):
        bbox_res = None
    else:
        bbox_res = f'{bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}'
    
    with open(outputPath, 'w') as fout:
        fout.write(bbox_res)
