import os
import time
from zipfile import ZipFile
import requests
from PySide2 import QtCore, QtWidgets

class Updater(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.version = '1.5.5'
        self.github = 'https://raw.githubusercontent.com/boyratata/song/update.py'
        self.zipfile = 'https://github.com/boyratata/song/archive/refs/heads/main.zip'
        self.update_checker()

    def update_checker(self):
        print('Checking for updates...')
        time.sleep(2)
        
        code = requests.get(self.github).text
        if "self.version = '1.5.5'" in code:
            print('This version is up to date!')
        else:
            print('Your version of Luna Token Grabber is outdated!')
            self.update()

    def update(self):
        print('Updating...')
        new_version_source = requests.get(self.zipfile)
        with open("Luna-Grabber-main.zip", 'wb')as zipfile:
            zipfile.write(new_version_source.content)
        with ZipFile("Luna-Grabber-main.zip", 'r') as filezip:
            filezip.extractall(path=os.path.join(os.path.expanduser("~"), "Desktop"))
        os.remove("Luna-Grabber-main.zip")
        print('The new version is now on your desktop.\nUpdate Complete!')

    def closeEvent(self, event):
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    updater = Updater()
    updater.close()
    app.exec_()

