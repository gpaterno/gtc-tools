#!/usr/bin/env python
#
# GTC Updater
# (c) 2012 Giuseppe "Gippa" Paterno' (gpaterno@gpaterno.com)
#     2012 Alessandro "alorenzi" Lorenzi (alorenzi@garl.ch)
#
# Tool to update the Gippa Thin Client (GTC) when installed
# in a partition or USB disk, so that less management is required
# during updates :)
#
# * Load config from /etc/liveimg.conf
# * Check if root (has to be run as root via sudo)
# * Check connectivity and reachability of the server
# * Check that RELEASE has an higher number of what I have
# * Try to mount rw the /cdrom (otherwise it's a real CD, need to update
#   partition or USB disk)
# * Delete if exists, and create temp dir in /cdrom (don't occupy mem for nothihg)
# * Download ISO file and signature file
# * Check signature file against ISO for corruption/modifications (security)
# * Open loop iso image and copy casper/* to /cdrom/casper
# * remount ro /cdrom
# * Done :)
#

import os
import sys
import re
import shutil
import logging
import pycurl
import hashlib
import subprocess
import glob
import shutil
from ctypes import *
from time import sleep
from tempfile import mkdtemp
import ConfigParser
import re


def getconf():
	# Take configuration from conf file
	# ./global.ini first, then /etc/gtc/global.ini

	conffiles  = ['/etc/gtc/global.ini', os.getcwd() + '/global.ini']
	conf_found = 0

	## Get Config File
	for conf in conffiles:
		if os.path.isfile(conf):
			myconfig   = conf
			conf_found = 1

	if conf_found == 0:
		logger.debug("Unable to find configuration files")
		return (0)

	conf = ConfigParser.RawConfigParser()
	conf.read( myconfig )

	global localrelease, localiso, remoteiso, remoterelease, releasename, isoname, disklbl, tmpdir, mountlocation

	if (conf.has_option("gtc","mountlocation") ):
		mountlocation = conf.get("gtc","mountlocation")
	else:
		mountlocation = "/isodevice/"



	# Take the conf from the file or choose a default


	if (conf.has_option("gtc","releasename") ):
		releasename = conf.get("gtc","releasename")
	else:
		releasename = "gtc.release"

	localrelease="/%s/gtc/%s" % (mountlocation, releasename)

	if (conf.has_option("gtc","isoname") ):
		isoname = conf.get("gtc","isoname")
	else:
		isoname = "gtc.iso"
	localiso = "%s/gtc/%s"% (mountlocation,isoname)
		     
		     
	if (conf.has_option("gtc","remoteiso") ):
		remoteiso = "%s/%s" % (conf.get("gtc","remoteiso"), isoname)
	else:
		remoteiso="http://gtc.garl.ch/iso/%s" %  isoname

		     
	if (conf.has_option("gtc","remoterelease") ):
		remoterelease = conf.get("gtc","releaselocation")+ "/" + releasename
	else:
		remoterelease="http://gtc.garl.ch/conf/%s" % (releasename)

		     
	if (conf.has_option("gtc","disklbl") ):
		disklbl = conf.get("gtc","disklbl")
	else:
		disklbl="GTC"
		
	return(1)


def cleanup():
	# delete tmp dir, !!! use before exit !!!
	try:
		for filename in glob.glob("%s/tmp/update*" % mountlocation):
			shutil.rmtree(filename)
	except:
		logger.error("Error cleanup")
		return(0)

	return(1)


def ckroot():
	# Verify if root

	from getpass import getuser
	if (getuser()!="root"):
		logger.error("You are not root!")
		logger.error("Try su or sudo")
		return 0
	# Try to perform a sudo? 
	return 1

def dl_progress(download_t, download_d, upload_t, upload_d):
	# Function for pycurl
	if float(download_t) != 0:
	    percentage = float(download_d)*100/float(download_t)
	    print "Downloading: %s%% \r" % int(percentage),

    

def download_config():
	# download release file
	try:
		logger.debug("Attempting to download conf " )
		conf = open("%s/%s"%(tmpdir, releasename), "wb")
		dwnld = pycurl.Curl()
		dwnld.setopt(pycurl.URL, remoterelease)
		dwnld.setopt(pycurl.NOPROGRESS, 0)
		dwnld.setopt(pycurl.PROGRESSFUNCTION, dl_progress)
		dwnld.setopt(pycurl.WRITEDATA, conf)
		dwnld.perform()
		print ""		# print empty line
		dwnld.close()
		conf.close()
	except pycurl.error, e:
		logger.error("Download failed: %s" % e[1])
		return(0)
		
	return(1)
		


def create_tmpdir(base=None):
	# Creating tmp dir
	# /isodevice/tmp/update*
	# base is path where create tmp directory

	global tmpdir
	# Verify exist the mount location
	if base==None:
		base="%s/tmp"%mountlocation
		
	if os.path.exists(base) ==False:
		try:
			os.mkdir(base)
		except:
			logger.error("Error creating temp dir" )
			return 0
	
	try:
		tmpdir = mkdtemp(prefix='update', dir=base)
	except:
		logger.error("Unable to create temp dir" )
		return False
	logger.debug("tmpdir = %s" %tmpdir)
	return 1

def ckrelease():
	# control if local release is old
	# return value  0 error
	#               1 the system is running current release
	#               2 the system is running an old release
	logger.debug("Comparing %s with %s/%s" % (localrelease, tmpdir, releasename))

	try:
		conf = ConfigParser.RawConfigParser()
		conf.read("%s/%s"%(tmpdir, releasename))

		if os.path.isfile(localrelease):
			conf_old=ConfigParser.RawConfigParser()
			conf_old.read(localrelease)
			local_releasedate = conf_old.getint("gtc","release")
		else:
			logger.debug("No local release file")
			local_releasedate = 0

		if (conf.getint("gtc","release")<=local_releasedate):
			logger.error("You are running an up-to-date verson")
			return (2)
			
	except:
		logger.error("Unable to process config %s/%s" % (tmpdir, releasename))
		return (False)
	
	print("Your release is old.")
	return (True)

def downloadiso():
	# download ISO from server
	try:
		logger.debug("Attempting to download ISO from %s" % remoteiso )
		iso = open("%s/%s"%(tmpdir, isoname), "wb")
		dwnld = pycurl.Curl()
		dwnld.setopt(pycurl.URL, remoteiso)
		dwnld.setopt(pycurl.NOPROGRESS, 0)
		dwnld.setopt(pycurl.PROGRESSFUNCTION, dl_progress)
		dwnld.setopt(pycurl.WRITEDATA, iso)
		dwnld.perform()
		print ""		# print empty line
		dwnld.close()
		iso.close()
	except pycurl.error, e:
		logger.error("Download failed: %s" % e[1])
		return False
	finally:
		logger.debug("Download completed")
	return True


		
def cksumiso():
	# check iso sha1 hash
	try: 
		logger.debug("Check sha1 iso")
		isohash = hashlib.sha1(open("%s/%s"%(tmpdir, isoname), "rb").read()).hexdigest()
	except:
		logger.error("Error calculating checksum" )

	
	try:
		conf = ConfigParser.RawConfigParser()
		conf.read("%s/%s"%(tmpdir, releasename))
	except:
		logger.error("Error reading config ")

	
	try:
		if (conf.get("gtc","sha1") != isohash):
			logger.error("Error downloading iso, corrupted.")
	except:
		logger.error("Error reading config")
		
	
	logger.debug("ckiso OK")
	
def replace_iso():
	# Replace iso with new version.
	logger.debug("Replacing existing installation")
	
	try:	
		if subprocess.call(['mv', "%s/%s"%(tmpdir, isoname),  localiso]) != 0:
			logger.error("Unable to replace the conf file")
			return (False)
		
		if subprocess.call(['mv', "%s/%s"%(tmpdir, releasename), localrelease ]) != 0:
			logger.error("Unable to replace the conf file")
			return False
	except:
		logger.error("Error moving file ")
		return False

		
	logger.debug("Replaced.")

def mklauncher():
	logger.info("start making launcher")
	desktop_content = "[Desktop Entry] \nName=Update the system \nComment= \nExec=/usr/sbin/gtc-update -i \nIcon=/usr/share/pixmaps/garl.png\nTerminal=true\nType=Application\nStartupNotify=true"

	
		
	try:
		desktop_file=open("/usr/share/applications/gtc-update.desktop","w")
		desktop_file.write(desktop_content)
		desktop_file.close()
	except:
		logger.error("ERROR while writing desktop file")
		return False

	try:
		# Modify gtc.gschema.override
		gschema_file=open("/usr/share/glib-2.0/schemas/gtc.gschema.override", "r")
		newcontent = ""
		for line in gschema_file:
				fav = re.search("favorites", line)
				yetexists =  re.search("'gtc-update.desktop'", line)
				# modify line "favorites" if gtc-update.desktop not exists 
				if fav!= None and yetexists == None:
						line = re.sub("]", ", 'gtc-update.desktop']",line)
				newcontent+=line
		gschema_file.close()

		# writing new gtc.gschema.override
		gschema_file=open("/usr/share/glib-2.0/schemas/gtc.gschema.override", "w")
		gschema_file.write(newcontent)
		gschema_file.close()
	except:
		logger.error("ERROR while writing gtc.gschema.override")
		return False

	try:
		subprocess.call("glib-compile-schemas /usr/share/glib-2.0/schemas/")
	except:
		logger.error("error while compiling glib schema")
		return False

	return True


def cmdline():
	# OLD
	# exec all in a command line.
	## Loading config
	getconf()
	## Welcome msg and warning
	logger.info("Checking for upgrades, make sure you're connected to the network and you have your power adapter connected.")

	
	if ckroot() == False:
		exit (0)
	create_tmpdir()
	download_config()
	ckrelease()
	downloadiso()
	cksumiso()
	replace_iso()
	
	cleanup()	
	
	logger.info("All done.")
	logger.info("Please reboot ASAP!")


def helper():
	# print a helper
	logger.error("TODO helper")
	logger.error("gtc-updater [-c] [-i] [-h]")
	logger.error(" -c Check updates and if updates are presents create a desktop icon")
	logger.error(" -i Install updates")
	logger.error(" -h This message")
	exit(1)

def check_updates():
	print "halo"
	# check if updates are available  
	## Loading config
	logger.info("Checking for upgrades, make sure you're connected to the network and you have your power adapter connected.")

	if getconf()==False:
		exit(1)

	
	if create_tmpdir(base="/tmp")==False:
		exit(1)
	if download_config()==False:
		exit(1)

	rcode =ckrelease()
	if rcode==False:
		exit(1)
	elif rcode==2:
		exit(0)
	
		
	if mklauncher()==False:
		exit(1)
			
	if cleanup()==False:
		exit(1)
	
	logger.info("All done.")
	exit(0)

def install_updates():
	# function to (re)check if updates are available and install
	#  
	# TODO: Add progress bar
	# https://wiki.ubuntu.com/Unity/LauncherAPI#Progress

	if os.getuid():
		sudocmd = "/usr/bin/sudo"
		if not os.path.exists(sudocmd):
			logger.error("Cannot find sudo cmd")
			exit(1)		
			
		command = "{} {}".format(sudocmd, " ".join(sys.argv))
		command = command.split()
		retcode = subprocess.call(command)
		if retcode:
			print("something wrong happened")
			exit(1)
		exit(0)

	if getconf()==False:
		exit(1)

	
	if create_tmpdir()==False:
		exit(1)
		
	if download_config()==False:
		exit(1)
		
	if ckrelease()==False:
		exit(1)
		
	if downloadiso()==False:
		exit(1)

	if cksumiso()==False:
		exit(1)
	
	if replace_iso()==False:
		exit(1)
			
	if cleanup()==False:
		exit(1)
	
	logger.info("All done.")
	exit(0)
	
	exit(0)






if __name__ == "__main__":
	# STARTS HERE
	import sys
	import os
	import subprocess
	import optparse

	
	## Setup logging first
	logfmt = " %(levelname)s: %(message)s"
	logging.basicConfig(format=logfmt, level=logging.DEBUG)
	global logger
	logger = logging.getLogger("gtc-updater")

	
	# parsing opts
	# -c Check updates and if updates are presents create a desktop icon
	# -i Install updates
	parser = optparse.OptionParser()
	parser.add_option("-c", nargs=0)
	parser.add_option("-i", nargs=0)
	(options, args) = parser.parse_args()

	if options.c != None:
		check_updates()
	elif options.i != None:
		install_updates()
	else:
		helper()
