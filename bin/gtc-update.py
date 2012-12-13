#!/usr/bin/python
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
import shutil
import logging
import pycurl
import hashlib
import subprocess
from ctypes import *

from tempfile import mkdtemp
import ConfigParser
	

def getconf():
	conffiles  = ['/etc/gtc/global.ini', os.getcwd() + '/global.ini']
	conf_found = 0

	## Get Config File
	for conf in conffiles:
		if os.path.isfile(conf):
			myconfig   = conf
			conf_found = 1

	if conf_found == 0:
		print "Unable to find configuration files"
		sys.exit(1)

	conf = ConfigParser.RawConfigParser()
	conf.read( myconfig )

	global logfmt, localrelease, remoteiso, remoterelease, releasename, isoname, disklbl, tmpdir, mountlocation

	


	if (conf.has_option("gtc","logfmt") ):
		logfmt = conf.get("gtc","logfmt")
	else:
		logfmt     = "%(levelname)s: %(message)s"


	if (conf.has_option("gtc","mountlocation") ):
		mountlocation = conf.get("gtc","mountlocation")
	else:
		mountlocation = "/mnt"


	if (conf.has_option("gtc","releasename") ):
		releasename = conf.get("gtc","releasename")
	else:
		releasename = "gtc.release"

	if (conf.has_option("gtc","isoname") ):
		isoname = conf.get("gtc","isoname")
	else:
		isoname = "gtc.iso"


		     
	if (conf.has_option("gtc","localconf") ):
		localrelease = "%s/%s/%s" %(mountlocation, conf.get("gtc","") , releasename)
	else:
		localrelease="%s/etc/%s" % (mountlocation, releasename)
		     
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




def ckroot():
	from getpass import getuser
	if (getuser()!="root"):
		logger.error("You are not root!")
		logger.error("Try su or sudo")
		exit(1)
	logger.debug("You are root. Yuppi!")

def dl_progress(download_t, download_d, upload_t, upload_d):
	if float(download_t) != 0:
	    percentage = float(download_d)*100/float(download_t)
	    print "Downloading: %s%% \r" % int(percentage),

def download_config():
	
	# download config
	try:
		logger.debug("Attempting to download conf " )
		conf = open("%s/%s"%(tmpdir, releasename), "wb")
		dwnld = pycurl.Curl()
		dwnld.setopt(pycurl.URL, remoterelease)
		dwnld.setopt(pycurl.NOPROGRESS, 0)
		dwnld.setopt(pycurl.PROGRESSFUNCTION, dl_progress)
		dwnld.setopt(pycurl.WRITEDATA, conf)
		dwnld.perform()
	except pycurl.error, e:
		logger.error("Download failed: %s" % e[1])
		exit(1)
	finally:
		print ""        # print empty line
		dwnld.close()
		conf.close()


def mount_device():
	if subprocess.call(['mount', "-L" , disklbl, mountlocation]) != 0:
		logger.error("Unable to mount the ISO image")
		exit(1)

def create_tmpdir():
	global tmpdir
	tmpdir = mkdtemp(prefix='update', dir="%s/tmp" %mountlocation)

def ckrelease():
	# confronto tra la versione sul server e versione installata
	conf = ConfigParser.RawConfigParser()
	conf.read("%s/%s"%(tmpdir, releasename))

	conf_old=ConfigParser.RawConfigParser()
	conf_old.read(localrelease)

	if (conf.getint("gtc","release")<=conf_old.getint("gtc","release")):
		logger.error("You are running an up-to-date verson!")
		logger.error("Be happy!")
		exit(1)
	logger.debug("Your release is old. Go on.")

def downloadiso():
	# download ISO
	try:
		logger.debug("Attempting to download ISO " )
		iso = open("%s/%s"%(tmpdir, isoname), "wb")
		dwnld = pycurl.Curl()
		dwnld.setopt(pycurl.URL, remoteiso)
		dwnld.setopt(pycurl.NOPROGRESS, 0)
		dwnld.setopt(pycurl.PROGRESSFUNCTION, dl_progress)
		dwnld.setopt(pycurl.WRITEDATA, iso)
		dwnld.perform()
		print ""        # print empty line
		dwnld.close()
		iso.close()
	except pycurl.error, e:
		logger.error("Download failed: %s" % e[1])
		exit(1)
	finally:
		logger.debug("Download completed")


		
def cksumiso():
	
	logger.debug("Check sha1 iso")
	isohash = hashlib.sha1(open("%s/%s"%(tmpdir, isoname), "rb").read()).hexdigest()

	conf = ConfigParser.RawConfigParser()
	conf.read("%s/%s"%(tmpdir, releasename))
	
	if (conf.get("gtc","sha1") != isohash):
		logger.error("Error downloading iso, corrupted.")
		exit(1)
	logger.debug("ckiso OK")
	
def replace_iso():
	logger.debug("Replacing existing installation")
	
	if subprocess.call(['mv', "%s/%s"%(tmpdir, isoname),  "%s/%s"% (mountlocation,isoname)]) != 0:
		logger.error("Unable to replace the conf file")
		exit(1)
		
	if subprocess.call(['mv', "%s/%s"%(tmpdir, releasename), localrelease ]) != 0:
		logger.error("Unable to replace the conf file")
		exit(1)

		
	logger.debug("Replaced.")



if __name__ == '__main__':
	getconf()

	logging.basicConfig(format=logfmt, level=logging.DEBUG)
	logger = logging.getLogger("gtc-updater")

	## Welcome msg and warning
	logger.info("Checking for upgrades, make sure you're connected to the network and you have your power adapter connected.")

	
	ckroot()
	mount_device()
	create_tmpdir()
	download_config()
	ckrelease()
	downloadiso()
	cksumiso()
	replace_iso()
	
	logger.info("All done.")
	logger.info("Please reboot ASAP!")



