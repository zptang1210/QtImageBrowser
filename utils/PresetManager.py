import os
import sys
from PyQt5 import QtWidgets
from utils.transformers.presets.registeredPresets import presets

class PresetManager:

    PRESET_REGISTRATION_FILE = os.path.join('utils', 'transformers', 'presets', 'registeredPresets.json')

    def __init__(self, presetActionTriggered):
        self.presetList = presets
        self.presetActionTriggered = presetActionTriggered

    def generatePresetMenu(self, parentMenu, presets):
        parentMenu.setToolTipsVisible(True)
        for keyName in presets.keys():
            item = presets[keyName]
            if 'preset' in item.keys():
                action = QtWidgets.QAction(item['name'], parentMenu)
                action.triggered.connect((lambda checked, fileName=item['file']: self.presetActionTriggered(fileName)))
                action.setToolTip(item['description'])
                parentMenu.addAction(action)
            else:
                subMenu = parentMenu.addMenu(keyName)
                self.generatePresetMenu(subMenu, presets[keyName])

    def getPreset(self, fileName):
        with open(fileName, 'r') as fin:
            script = fin.read()
        return script


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv) 
    menu = QtWidgets.QMenu()
    presetManager = PresetManager()
    presetManager.generatePresetMenu(menu, presetManager.presetList)
    menu.show()
    sys.exit(app.exec_())