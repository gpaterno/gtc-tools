#!/usr/bin/env python
import gtcupdate
from PyQt4 import QtCore, QtGui
from update import *
import logging

class MainWindow (object):
 
	def __init__(self):
		self.app = QtGui.QApplication([])
		self.Dialog = QtGui.QMainWindow()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self.Dialog)
		self.connections()
	 
	def connections(self):
		#BUTTON CONNECTIONS
		self.app.connect(self.ui.btn_update, QtCore.SIGNAL("clicked()"), self.update)
		 	 
	def run(self):
		self.Dialog.show()
		self.app.exec_()
	 
	def update(self):
		
		# function to (re)check if updates are available and install
		#  
		# TODO: Add progress bar
		# https://wiki.ubuntu.com/Unity/LauncherAPI#Progress

		self.insert("Getting config ...... ")
		if gtcupdate.getconf()==False:
			self.insert("FAIL\n")
			return False
		self.insert("DONE\n")

		self.insert("Creating tmp dir .... ")
		if gtcupdate.create_tmpdir()==False:
			self.insert("FAIL\n")
			return False
		self.insert("DONE\n")

		self.insert("Downloading config .. ")		
		if gtcupdate.download_config()==False:
			self.insert("FAIL\n")
			return False
		self.insert("DONE\n")
			
		if gtcupdate.ckrelease()==False:
			self.insert("FAIL\n")
			return False
		self.insert("DONE\n")

		self.insert("Downloading ISO ..... ")		
		if gtcupdate.downloadiso()==False:
			self.insert("FAIL\n")
			return False
		self.insert("DONE\n")

		self.insert("Verifing ISO ........ ")
		if gtcupdate.cksumiso()==False:
			self.insert("FAIL\n")
			return False
		self.insert("DONE\n")

		self.insert("Istalling GTC ....... ")	
		if gtcupdate.replace_iso()==False:
			self.insert("FAIL\n")
			return False
		self.insert("DONE\n")

		self.insert("Cleanup system ... ")		
		if gtcupdate.cleanup()==False:
			self.insert("FAIL\n")
			return False
		self.insert("DONE\n")
		
		return True
	 
	def insert(self, mex):
		if mex != "":
			self.ui.txt_output.insertPlainText(mex )

 
if __name__ == "__main__":
	
	
	window = MainWindow()
	window.run()
