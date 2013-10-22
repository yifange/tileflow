import sys
from PySide import QtCore, QtGui, QtOpenGL

try:
    from OpenGL.GL import *
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL textures",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)

class TileflowWidget(QtOpenGL.QGLWidget):

    coords = (
        ( ( +1, -1, -1 ), ( -1, -1, -1 ), ( -1, +1, -1 ), ( +1, +1, -1 ) ),
        ( ( +1, +1, -1 ), ( -1, +1, -1 ), ( -1, +1, +1 ), ( +1, +1, +1 ) ),
        ( ( +1, -1, +1 ), ( +1, -1, -1 ), ( +1, +1, -1 ), ( +1, +1, +1 ) ),
        ( ( -1, -1, -1 ), ( -1, -1, +1 ), ( -1, +1, +1 ), ( -1, +1, -1 ) ),
        ( ( +1, -1, +1 ), ( -1, -1, +1 ), ( -1, -1, -1 ), ( +1, -1, -1 ) ),
        ( ( -1, -1, +1 ), ( +1, -1, +1 ), ( +1, +1, +1 ), ( -1, +1, +1 ) )
    )
    SCALE = 0.7
    SPREAD_IMAGE = 0.14
    FLANK_SPREAD = 0.4
    VISIBLE_TILES = 3

    clicked = QtCore.Signal()

    def __init__(self, parent):
        QtOpenGL.QGLWidget.__init__(self, parent)

        # self.clearColor = QtCore.Qt.black
        self.xRot = 0
        self.yRot = 0
        self.zRot = 0
        self.mWidth = 0
        self.clearColor = QtGui.QColor()
        self.lastPos = QtCore.QPoint()
        self.obj = None

    # def freeGLResources(self):
    #     TileflowWidget.refCount -= 1
    #     if TileflowWidget.refCount == 0:
    #         self.makeCurrent()
    #         glDeleteLists(self.__class__.obj, 1)

    def minimumSizeHint(self):
        return QtCore.QSize(50, 50)

    def sizeHint(self):
        return QtCore.QSize(200, 200)

    def rotateBy(self, xAngle, yAngle, zAngle):
        self.xRot = (self.xRot + xAngle) % 5760
        self.yRot = (self.yRot + yAngle) % 5760
        self.zRot = (self.zRot + zAngle) % 5760
        self.updateGL()

    def setClearColor(self, color):
        self.clearColor = color
        self.updateGL()

    def initializeGL(self):
        if not self.obj:
            self.tiles = []
            for i in range(6):
                self.tiles.append(Tile(self.bindTexture(QtGui.QPixmap("images/side%d.png" % (i + 1)))))
            self.obj = self.makeObject()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_TEXTURE_2D)

    def paintGL(self):
        self.qglClearColor(self.clearColor)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslated(0.0, 0.0, -10.0)
        glRotated(self.xRot / 16.0, 1.0, 0.0, 0.0)
        glRotated(self.yRot / 16.0, 0.0, 1.0, 0.0)
        glRotated(self.zRot / 16.0, 0.0, 0.0, 1.0)
        glCallList(self.obj)

    def resizeGL(self, width, height):
        mWidth = width
        imagew = width * 0.45 / TileflowWidget.SCALE / 2.0
        imageh = height * 0.45 / TileflowWidget.SCALE / 2.0

        glViewport(0, 0, width, height)
        ratio = width / height
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-ratio * TileflowWidget.SCALE, ratio * TileflowWidget.SCALE, -1 * TileflowWidget.SCALE, 1 * TileflowWidget.SCALE, 1, 3)
        # glMatrixMode(GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        dy = event.y() - self.lastPos.y()

        if event.buttons() & QtCore.Qt.LeftButton:
            self.rotateBy(8 * dy, 8 * dx, 0)
        elif event.buttons() & QtCore.Qt.RightButton:
            self.rotateBy(8 * dy, 0, 8 * dx)

        self.lastPos = QtCore.QPoint(event.pos())

    def mouseReleaseEvent(self, event):
        self.clicked.emit()

    def makeObject(self):
        dlist = glGenLists(1)
        glNewList(dlist, GL_COMPILE)
        offset = 3
        mid = 3
        # startPos = mid - VISIBLE_TILES
        # if startPos < 0:
        #     startPos = 0

        for i in range(0, mid):
            self.drawTile(i, i - offset, self.tiles[i])
        for i in range(5, mid, -1):
            self.drawTile(i, i - offset, self.tiles[i])
        # for i in range(6):
        #     self.drawTile(i, 0, self.tiles[i])
        glEndList()
        return dlist

    def drawTile(self, position, off, tile):
        matrix = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        trans = off * TileflowWidget.SPREAD_IMAGE
        f = off * TileflowWidget.FLANK_SPREAD
        if (f > TileflowWidget.FLANK_SPREAD):
            f = TileflowWidget.FLANK_SPREAD
        elif (f < -TileflowWidget.FLANK_SPREAD):
            f = -TileflowWidget.FLANK_SPREAD
        print f
        matrix[3] = -f
        matrix[0] = 1 - abs(f)
        sc = 0.38 * matrix[0]
        trans += f * 1

        print matrix
        glPushMatrix()
        glBindTexture(GL_TEXTURE_2D, tile.texture)

        glTranslatef(trans, 0, 0)
        glScalef(sc, sc, 1.0)
        glMultMatrixf(matrix)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        glTranslatef(0, -2, 0)
        glScalef(1, -1, 1)
        glColor4f(1, 1, 1, 0.5)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
        glColor4f(1, 1, 1, 1)

        glPopMatrix()

class Tile:
    def __init__(self, texture):
        self.texture = texture

class Window(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        mainLayout = QtGui.QHBoxLayout()
        self.glWidget = TileflowWidget(self)
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        self.setWindowTitle(self.tr("Tileflow"))



if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
