#!/usr/bin/env python

import sys
import math
from PySide import QtCore, QtGui, QtOpenGL
try:
    from OpenGL.GL import *
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL hellogl",
                            "PyOpenGL must be installed to run this example.",
                            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Default,
                            QtGui.QMessageBox.NoButton)
    sys.exit(1)

class Window(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.glWidget = GLWidget(self)

        mainLayout = QtGui.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        self.setLayout(mainLayout)
        self.setWindowTitle(self.tr("Coverflow"))

class GLWidget(QtOpenGL.QGLWidget):
    coords = (
        ( ( +1, -1, -1 ), ( -1, -1, -1 ), ( -1, +1, -1 ), ( +1, +1, -1 ) ),
        ( ( +1, +1, -1 ), ( -1, +1, -1 ), ( -1, +1, +1 ), ( +1, +1, +1 ) ),
        ( ( +1, -1, +1 ), ( +1, -1, -1 ), ( +1, +1, -1 ), ( +1, +1, +1 ) ),
        ( ( -1, -1, -1 ), ( -1, -1, +1 ), ( -1, +1, +1 ), ( -1, +1, -1 ) ),
        ( ( +1, -1, +1 ), ( -1, -1, +1 ), ( -1, -1, -1 ), ( +1, -1, -1 ) ),
        ( ( -1, -1, +1 ), ( +1, -1, +1 ), ( +1, +1, +1 ), ( -1, +1, +1 ) )
    )

    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.clearColor = QtCore.Qt.red
        self.xRot = 45
        self.yRot = 45
        self.zRot = 45
        self.obj = None
        self.textures = []
        # self.clearColor = QtGui.QColor()
        self.lastPos = QtCore.QPoint()

    def rotateBy(self, xAngle, yAngle, zAngle):
        self.xRot = (self.xRot + xAngle) % 5760
        self.yRot = (self.yRot + yAngle) % 5760
        self.zRot = (self.zRot + zAngle) % 5760
        self.updateGL()

    def minimumSizeHing(self):
        return QtCore.QSize(100, 50)

    def rotateBy(self, xAngle, yAngle, zAngle):
        pass

    def setClearColor(self, color):
        self.clearColor = color
        self.updateGL()

    def sizeHint(self):
        return QtCore.QSize(800, 400)

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

    def initializeGL(self):
        if not self.obj:
            self.textures = []
            for i in range(6):
                self.textures.append(self.bindTexture(QtGui.QPixmap("images/side%d.png" % (i + 1))))
            print self.textures
            self.obj = self.makeObject()

        glShadeModel(GL_FLAT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

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
        side = min(width, height)
        glViewport((width - side) / 2, (height - side) / 2, side, side)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-0.5, +0.5, +0.5, -0.5, 4.0, 15.0)
        glMatrixMode(GL_MODELVIEW)

    def makeObject(self):
        dlist = glGenLists(1)
        glNewList(dlist, GL_COMPILE)

        for i in range(6):
            glBindTexture(GL_TEXTURE_2D, self.textures[i])

            glBegin(GL_QUADS)
            for j in range(4):
                tx = {False: 0, True: 1}[j == 0 or j == 3]
                ty = {False: 0, True: 1}[j == 0 or j == 1]
                glTexCoord2d(tx, ty)
                glVertex3d(0.2 * GLWidget.coords[i][j][0],
                           0.2 * GLWidget.coords[i][j][1],
                           0.2 * GLWidget.coords[i][j][2])
            glEnd()

        glEndList()
        return dlist

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
