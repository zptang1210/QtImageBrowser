import os, sys
import time
import argparse
from utils.pathUtils import normalizePath
from utils.TransformCodeInterpreter import TransformCodeInterpreter
from configs.availTypesConfig import availTypes
from configs.availTypesConfig import modelClassDict

def argsParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', type=str, required=True, help='the path of the image collection on the server (e.g. ~\imgs\)')
    parser.add_argument('--model_type', type=str, required=True, help='the type of the image collection (folder, video, ppm)')
    parser.add_argument('--script_file', type=str, required=True, help='the path of the script for transformation')
    parser.add_argument('--result_name', type=str, required=True, help='the name for the result image collection')

    args = parser.parse_args()

    # print(args)
    return args

def checkArgs(args):
    try:
        args.model_path = normalizePath(os.path.expanduser(args.model_path))
        args.script_file = normalizePath(os.path.expanduser(args.script_file))
    except:
        print('invalid path for model or script.', file=sys.stderr)
        return False
    
    if not os.path.exists(args.model_path):
        print('model_path not exists', file=sys.stderr)
        return False
    if args.model_type not in availTypes:
        print('invalid model_type', file=sys.stderr)
        return False
    if not os.path.exists(args.script_file):
        print('script not exists', file=sys.stderr)
        return False
    return True


def createModel(path, name, type):
    modelClass = modelClassDict[type]
    try:
        model = modelClass(path, name, parentModel=None)
    except:
        return None
    else:
        return model

def runScript(rawCode, model, newCollectionName, rootSavePath):
    interpreter = TransformCodeInterpreter()
    model = interpreter.parseAndRun(rawCode, model, newCollectionName, rootSavePath=rootSavePath)
    return model

def runTransform():
    os.chdir(os.path.dirname(__file__))
    args = argsParser()

    flag = checkArgs(args)
    if not flag: 
        print('invalid args', file=sys.stderr)
        return False, None, None

    model = createModel(args.model_path,  str(time.time()), args.model_type)
    if model is None:
        print('failed to load the model', file=sys.stderr)
        return False, None, None
    
    try:
        with open(args.script_file, 'r') as fin:
            rawCode = fin.read()
    except:
        print('failed to read the script', file=sys.stderr)
        return False, None, None

    rootSavePath = normalizePath(os.path.join(os.path.dirname(__file__), 'tmp'))
    model = runScript(rawCode, model, args.result_name, rootSavePath)
    if model is None:
        print('failed to run the script', file=sys.stderr)
        return False, None, None
    
    return True, model.path, model.name



if __name__ == '__main__':
    # python transform.py --model_path=/home/zhipengtang/testData/batch_00002_0 --model_type=folder --script_file=./script.txt --result_name=tmp
    flag, path, name = runTransform()
    print('transform_finished', int(flag), path, name)
    

    



    
