#!/bin/python


from PyQt4 import QtCore, QtGui
import sys
from mainwindow import *
from lib import gtcupdate
 
class MainWindow (object):
	 
	def __init__(self):
		self.app = QtGui.QApplication([])
		self.Dialog = QtGui.QMainWindow()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self.Dialog)
		self.connections()

	 
	def connections(self):
		#BUTTON CONNECTIONS
		self.app.connect(self.ui.ckupdate, QtCore.SIGNAL("clicked()"), self.ckupdates)
		 
		 
	def run(self):
		self.Dialog.show()
		self.app.exec_()
		 
	def clear(self):
		self.ui.textEdit.clear()
		self.ui.htmlEdit.clear()
	 
	def ckupdates(self):
		rval = gtcupdate.getconf() 
		if rval != 1:
			self.ui.lbloutput.setText("Impossibile trovare il file di configurazione\n")
			self.ui.lbloutput.setText("Controlla l'esistenza di global.ini nella directory /etc/gtc/ \n")
			return(0)

		rval = gtcupdate.ckroot()
		if rval == 0:
			self.ui.lbloutput.setText("Devi essere amministratore per eseguire l'aggiornamento del GTC")
			return(0)

		rval = 	gtcupdate.mount_device()
		if rval == 0:
			self.ui.lbloutput.setText("Errore durante il mount del device")
			return(0)
					
		rval = gtcupdate.create_tmpdir()
		if rval == 0:
			self.ui.lbloutput.setText("Errore nella creazione della directory temporanea")
			return(0)

		rval = gtcupdate.download_config()
		if rval == 0:
			self.ui.lbloutput.setText("Errore nella creazione della directory temporanea")
			return(0)


		rval = gtcupdate.ckrelease()
		if rval == 0:
			self.ui.lbloutput.setText("Errore")
			return (0)
		elif rval == 1:
			self.ui.lbloutput.setText("La release e' aggiornata")
			return(0)
		elif rval == 2:
			self.ui.lbloutput.setText("Devi aggiornare!")

			
		 
	def toHtml(self):
		self.ui.htmlEdit.setHtml(self.ui.textEdit.toPlainText())
 
if __name__ == "__main__":
	import logging

	## Setup logging first
	logfmt = " %(levelname)s: %(message)s"
	logging.basicConfig(format=logfmt, level=logging.DEBUG)
	global logger
	logger = logging.getLogger("gtc-updater")

	window = MainWindow()
	window.run()
