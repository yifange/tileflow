import sys
import math
from PySide import QtCore, QtGui, QtOpenGL

try:
    from OpenGL import GLU, GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL textures",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)

class TileflowWidget(QtOpenGL.QGLWidget):

    GVertices = [
        -1.0, -1.0, 0.0,
        1.0, -1.0, 0.0,
        -1.0, 1.0, 0.0,
        1.0, 1.0, 0.0
    ]
    GTextures = [
        0.0, 1.0,
        1.0, 1.0,
        0.0, 0.0,
        1.0, 0.0
    ]
    SCALE = 0.7
    SPREAD_IMAGE = 0.14
    FLANK_SPREAD = 0.4
    VISIBLE_TILES = 3


    def __init__(self, parent):
        QtOpenGL.QGLWidget.__init__(self, parent)

        # self.clearColor = QtCore.Qt.black
        self.mWidth = 0
        self.clearColor = QtGui.QColor()
        self.lastPos = QtCore.QPoint()
        self.tiles = []
        self.max = 6
        self.offset = 3
        self.mWidth = 533

    def minimumSizeHint(self):
        return QtCore.QSize(533, 270)

    def sizeHint(self):
        return QtCore.QSize(533, 270)


    def setClearColor(self, color):
        self.clearColor = color
        self.updateGL()

    def initializeGL(self):
        for i in range(6):
            self.tiles.append(Tile(self.bindTexture(QtGui.QPixmap("images/side%d.png" % (i + 1)))))
        self.verticesBuffer = TileflowWidget.GVertices
        self.texturesBuffer = TileflowWidget.GTextures

    def paintGL(self):
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GLU.gluLookAt(0, 0, 2, 0, 0, 0, 0, 1, 0)
        GL.glDisable(GL.GL_DEPTH_TEST)

        GL.glClearColor(0, 0, 0, 0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glPushMatrix()
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        # offset = self.offset
        offset = self.offset
        if offset <= 0:
            offset = 0
        if offset > 5:
            offset = 5
        mid = int(math.floor(offset + 0.5))
        # startPos = mid - VISIBLE_TILES
        # if startPos < 0:
        #     startPos = 0

        for i in range(0, mid):
            self.drawTile(i, i - offset, self.tiles[i])
        for i in range(5, mid - 1, -1):
            self.drawTile(i, i - offset, self.tiles[i])

        GL.glPopMatrix()


    def resizeGL(self, width, height):
        mWidth = width
        imagew = width * 0.45 / TileflowWidget.SCALE / 2.0
        imageh = height * 0.45 / TileflowWidget.SCALE / 2.0

        GL.glViewport(0, 0, width, height)
        ratio = float(width) / height
        print ratio
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-ratio * TileflowWidget.SCALE, ratio * TileflowWidget.SCALE, -1 * TileflowWidget.SCALE, 1 * TileflowWidget.SCALE, 1, 3)
        self.verticesBuffer = [
            -ratio * TileflowWidget.SCALE, -TileflowWidget.SCALE, 0,
            ratio * TileflowWidget.SCALE, -TileflowWidget.SCALE, 0,
            -ratio * TileflowWidget.SCALE, TileflowWidget.SCALE, 0,
            ratio * TileflowWidget.SCALE, TileflowWidget.SCALE, 0
        ]
        # print self.verticesBuffer
        # glMatrixMode(GL_MODELVIEW)

    def mousePressEvent(self, event):
        self.lastPos = QtCore.QPoint(event.pos())

    def mouseMoveEvent(self, event):
        dx = event.x() - self.lastPos.x()
        print dx
        if event.buttons() & QtCore.Qt.LeftButton:
            self.offset += float(dx) * 6 / self.mWidth
            self.updateGL()

        self.lastPos = QtCore.QPoint(event.pos())

    def mouseReleaseEvent(self, event):
        pass

    def drawTile(self, position, off, tile):
        matrix = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        trans = off * TileflowWidget.SPREAD_IMAGE
        f = off * TileflowWidget.FLANK_SPREAD
        if (f > TileflowWidget.FLANK_SPREAD):
            f = TileflowWidget.FLANK_SPREAD
        elif (f < -TileflowWidget.FLANK_SPREAD):
            f = -TileflowWidget.FLANK_SPREAD

        matrix[3] = -f
        matrix[0] = 1 - abs(f)
        sc = 0.38 * matrix[0]
        trans += f * 1

        GL.glPushMatrix()
        GL.glBindTexture(GL.GL_TEXTURE_2D, tile.texture)
        GL.glTranslatef(trans, 0, 0)
        GL.glScalef(sc, sc, 1.0)
        GL.glMultMatrixf(matrix)

        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2d(1, 0)
        GL.glVertex3d(1, -1, 0)
        GL.glTexCoord2d(0, 0)
        GL.glVertex3d(-1, -1, 0)
        GL.glTexCoord2d(0, 1)
        GL.glVertex3d(-1, 1, 0)
        GL.glTexCoord2d(1, 1)
        GL.glVertex3d(1, 1, 0)
        GL.glEnd()

        GL.glTranslatef(0, -2.0, 0)
        GL.glScalef(1, -1, 1)
        GL.glColor4f(1, 1, 1, 0.5)
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2d(1, 0)
        GL.glVertex3d(1, -1, 0)
        GL.glTexCoord2d(0, 0)
        GL.glVertex3d(-1, -1, 0)
        GL.glTexCoord2d(0, 1)
        GL.glVertex3d(-1, 1, 0)
        GL.glTexCoord2d(1, 1)
        GL.glVertex3d(1, 1, 0)
        GL.glEnd()
        GL.glColor4f(1, 1, 1, 1)

        GL.glPopMatrix()

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
