import os
import PySide6
from PySide6.QtWidgets import QApplication, QLabel
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path


from PySide6.QtWidgets import *
from PySide6.QtGui import *
import sys
from PySide6.QtCore import Qt
from real_ui import RealMainWindow

app = QApplication(sys.argv)

#window = NodeWindow()
window = RealMainWindow()
app.setStyle(QStyleFactory.create("Fusion"))

app.exec()