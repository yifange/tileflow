import sys
import glob
from PySide import QtGui
from tileflow import TileflowWidget


class Window(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        mainLayout = QtGui.QHBoxLayout()
        res_list = sorted(glob.glob("images/*.png"))
        # res_list = ["images/side" + str(ind + 1) + ".png" for ind in range(6)]
        self.glWidget = TileflowWidget(self, res_list)
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        self.setWindowTitle(self.tr("Tileflow"))

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
