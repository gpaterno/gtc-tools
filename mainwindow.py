# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created: Fri Dec 14 13:32:45 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayoutWidget = QtGui.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(110, 80, 331, 161))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.lbloutput = QtGui.QLabel(self.verticalLayoutWidget)
        self.lbloutput.setText(_fromUtf8(""))
        self.lbloutput.setObjectName(_fromUtf8("lbloutput"))
        self.verticalLayout.addWidget(self.lbloutput)
        self.ckupdate = QtGui.QPushButton(self.verticalLayoutWidget)
        self.ckupdate.setObjectName(_fromUtf8("ckupdate"))
        self.verticalLayout.addWidget(self.ckupdate)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuGTC_Updater = QtGui.QMenu(self.menubar)
        self.menuGTC_Updater.setObjectName(_fromUtf8("menuGTC_Updater"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuGTC_Updater.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.ckupdate.setText(QtGui.QApplication.translate("MainWindow", "ckupdate", None, QtGui.QApplication.UnicodeUTF8))
        self.menuGTC_Updater.setTitle(QtGui.QApplication.translate("MainWindow", "GTC Updater", None, QtGui.QApplication.UnicodeUTF8))

