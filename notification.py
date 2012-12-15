#!/bin/python
# giusto un'idea...

import sys
from PyQt4 import QtCore
from PyQt4 import QtGui


class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, parent)

        self.setIcon(QtGui.QIcon("icon.jpg"))

        self.iconMenu = QtGui.QMenu(parent)
        appckupdate = self.iconMenu.addAction("Check Update")
        appupdate = self.iconMenu.addAction("Install new version")
        self.setContextMenu(self.iconMenu)

        self.connect(appckupdate,QtCore.SIGNAL('triggered()'),self.guickupdate)
        self.connect(appupdate,QtCore.SIGNAL('triggered()'),self.guiupdate)
        self.show()


    def guickupdate(self):
	self.showMessage("Update your system","There is an update available", msecs=10000)
	self.connect(self.messageClicked(),QtCore.SIGNAL('triggered()'),self.cliccato)

    def cliccato(self):
	print ("Cliccato sul baloon")

    def guiupdate(self):
	sys.exit(0)

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    trayIcon = SystemTrayIcon()
    trayIcon.show()

    sys.exit(app.exec_())
