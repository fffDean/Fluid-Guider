import os
import PySide6
dirname = os.path.dirname(PySide6.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
if __name__ == '__main__':
    from PySide6.QtWidgets import *
    import sys
    from gui_test.test1_ui2 import mdiWindow

    app = QApplication(sys.argv)
    # window = HoleWindow()
    window = mdiWindow()
    app.setStyle(QStyleFactory.create("Fusion"))

    app.exec()
