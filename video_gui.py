# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'video_capture.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("Đọc Thủ Ngữ")
        MainWindow.resize(800, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.btnStart = QtWidgets.QPushButton(self.centralwidget)
        self.btnStart.setGeometry(QtCore.QRect(650, 10, 120, 50))
        font = QtGui.QFont()
        font.setFamily("DejaVu Math TeX Gyre")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnStart.setFont(font)
        self.btnStart.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnStart.setAutoFillBackground(False)
        self.btnStart.setObjectName("btnStart")
        self.btnStart.setStyleSheet("background-color: lightgreen")
        self.rbt_audio_en = QtWidgets.QRadioButton(self.centralwidget)
        self.rbt_audio_en.setGeometry(QtCore.QRect(650, 150, 120, 30))
        font = QtGui.QFont()
        font.setFamily("DejaVu Serif")
        self.rbt_audio_en.setFont(font)
        self.rbt_audio_en.setObjectName("rbt_audio_en")
        self.btnExit = QtWidgets.QPushButton(self.centralwidget)
        self.btnExit.setGeometry(QtCore.QRect(650, 80, 120, 50))
        font = QtGui.QFont()
        font.setFamily("DejaVu Math TeX Gyre")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnExit.setFont(font)
        self.btnExit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btnExit.setAutoFillBackground(False)
        self.btnExit.setObjectName("btnExit")
        self.btnExit.setStyleSheet("background-color: red")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(0, 25, 640, 375))
        self.graphicsView.setObjectName("graphicsView")
        self.txtResult = QtWidgets.QLabel(self.centralwidget)
        self.txtResult.setGeometry(QtCore.QRect(0, 0, 640, 25))
        self.txtResult.setAlignment(QtCore.Qt.AlignCenter)
        self.txtResult.setObjectName("txtResult")
        font.setFamily("DejaVu Math TeX Gyre")
        font.setPointSize(20)
        font.setBold(True)
        # font.setWeight(75)
        self.txtResult.setFont(font)

        self.txtImage = QtWidgets.QLabel(self.centralwidget)
        self.txtImage.setGeometry(QtCore.QRect(0, 25, 640, 400))
        self.txtImage.setAlignment(QtCore.Qt.AlignCenter)
        self.txtImage.setObjectName("txtImage")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 780, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnStart.setText(_translate("MainWindow", "Bắt đầu"))
        self.rbt_audio_en.setText(_translate("MainWindow", "Tắt âm"))
        self.btnExit.setText(_translate("MainWindow", "Thoát"))
        self.txtResult.setText(_translate("MainWindow", ""))
        self.txtImage.setText(_translate("MainWindow", "Image"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
