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
	

MS_REMOUNT = 32
MS_RDONLY  = 1
LINUX_LIBC = "libc.so.6"

partition = "/dev/sda1"
logfmt     = "%(levelname)s: %(message)s"
isoname="gtc.iso"
confname="gtc.conf"
host="gtc.garl.ch"
isolocation="http://%s/iso/%s" % (host, isoname)
conflocation="http://%s/conf/%s" % (host, confname)
tmpdir     = mkdtemp()

def dl_progress(download_t, download_d, upload_t, upload_d):
	if float(download_t) != 0:
	    percentage = float(download_d)*100/float(download_t)
	    print "Downloading: %s%% \r" % int(percentage),

def download_config():
	
	# download config
	try:
		logger.debug("Attempting to download conf " )
		conf = open("%s/%s"%(tmpdir, confname), "wb")
		dwnld = pycurl.Curl()
        	dwnld.setopt(pycurl.URL, conflocation)
		dwnld.setopt(pycurl.NOPROGRESS, 0)
        	dwnld.setopt(pycurl.PROGRESSFUNCTION, dl_progress)
		dwnld.setopt(pycurl.WRITEDATA, conf)
		dwnld.perform()
	except pycurl.error, e:
		logger.error("Download failed: %s" % e[1])
	finally:
		print ""        # print empty line
		dwnld.close()
		conf.close()


def mount_device():
	if subprocess.call(['mount', partition, "/mnt"]) != 0:
		logger.error("Unable to mount the ISO image")
		exit(1)

def ckversion():
	# confronto tra la versione sul server e versione installata
	conf = ConfigParser.RawConfigParser()
	conf.read("%s/%s"%(tmpdir, confname))

	conf_old=ConfigParser.RawConfigParser()
	conf_old.read("/mnt/etc/liveimg.conf")

	if (conf.getint("gtc","version")<=conf_old("gtc","version")):
		logger.error("You are running an up-to-date verson!")
		logger.error("Be happy!")
		exit(1)
	logger.debug("Your version is old. Go on.")

def downloadiso():
	# download ISO
	try:
		logger.debug("Attempting to download ISO " )
		iso = open("%s/%s"%(tmpdir, isoname), "wb")
		dwnld = pycurl.Curl()
        	dwnld.setopt(pycurl.URL, isolocation)
		dwnld.setopt(pycurl.NOPROGRESS, 0)
        	dwnld.setopt(pycurl.PROGRESSFUNCTION, dl_progress)
		dwnld.setopt(pycurl.WRITEDATA, iso)
		dwnld.perform()
	except pycurl.error, e:
		logger.error("Download failed: %s" % e[1])
		exit(1)
	finally:
		print ""        # print empty line
		dwnld.close()
		iso.close()

def replace_iso():
	logger.debug("Replacing existing installation")
	if subprocess.call(['mv', "%s/%s"%(tmpdir, isoname), "/mnt"]) != 0:
		logger.error("Unable to replace the ISO image")
		exit(1)


if __name__ == '__main__':
	logging.basicConfig(format=logfmt, level=logging.DEBUG)
	logger = logging.getLogger("gtc-updater")

	## Welcome msg and warning
	logger.info("Checking for upgrades, make sure you're connected to the network and you have your power adapter connected.")

    ## Load the libc to call mount
	libc = cdll.LoadLibrary(LINUX_LIBC)

	
	mount_device()
	download_config()
	ckversion()
	download_iso()
	replace_iso()
	
	logger.info("All done.")



