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
import re
import shutil
import logging
import pycurl
import hashlib
import subprocess
import glob
import shutil
from ctypes import *

from tempfile import mkdtemp
import ConfigParser
	
def cleanup():
	# rimuove le directory temporanee,
	# da utilizzare prima di uscire dal programma
	for filename in glob.glob("%s/tmp/update*" %mountlocation)
		shutil.rmtree(filename)

def getconf():
	# legge i parametri dal file di configurazione, prima dal file locale,
	# poi dal file in etc

	conffiles  = ['/etc/gtc/global.ini', os.getcwd() + '/global.ini']
	conf_found = 0

	## Get Config File
	for conf in conffiles:
		if os.path.isfile(conf):
			myconfig   = conf
			conf_found = 1

	if conf_found == 0:
		print "Unable to find configuration files"
		cleanup()
		exit(1)

	conf = ConfigParser.RawConfigParser()
	conf.read( myconfig )

	global logfmt, localrelease, remoteiso, remoterelease, releasename, isoname, disklbl, tmpdir, mountlocation

	

	logfmt     = "%(levelname)s: %(message)s"
	localrelease="%s/%s" % (mountlocation, releasename)

	# per ogni parametro prevedo un default.

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

	localrelease="%s/%s" % (mountlocation, releasename)
		     
		     
	if (conf.has_option("gtc","remoteiso") ):
		remoteiso = "%s/%s" % (conf.get("gtc","remoteiso"), isoname)
		logger.debug("Remote iso set to %s" % remoteiso)
	else:
		remoteiso="http://gtc.garl.ch/iso/%s" %  isoname
		logger.debug("Loading default ISO location %s" % remoteiso)

		     
	if (conf.has_option("gtc","remoterelease") ):
		remoterelease = conf.get("gtc","releaselocation")+ "/" + releasename
	else:
		remoterelease="http://gtc.garl.ch/conf/%s" % (releasename)

		     
	if (conf.has_option("gtc","disklbl") ):
		disklbl = conf.get("gtc","disklbl")
	else:
		disklbl="GTC"




def ckroot():
	# check root, controllo che il tool stia girando
	# in modalita' superuser.

	from getpass import getuser
	if (getuser()!="root"):
		logger.error("You are not root!")
		logger.error("Try su or sudo")
		cleanup()
		exit(1)
	logger.debug("You are root. Yuppi!")

def dl_progress(download_t, download_d, upload_t, upload_d):
	# funzione di comodo per pycurl
	if float(download_t) != 0:
	    percentage = float(download_d)*100/float(download_t)
	    print "Downloading: %s%% \r" % int(percentage),

def download_config():
	# Download del file di release dal server.
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
		cleanup()
		exit(1)
	finally:
		print ""        # print empty line
		dwnld.close()
		conf.close()


def mount_device():
	# controllo se il dispositivo "GTC" e' gia montato
	# altrimenti lo monto.
	#if os.path.ismount(mountlocation):
	#	return 
	
	## Check if it's not already mounted, maybe not finished
	## right
	allmounts = open("/proc/mounts").readlines()
        for mount in allmounts:
           if re.search(mountlocation, mount, re.IGNORECASE):
	      device = mount.split(" ")[0]
              logger.warning("%s already mounted on %s, skip" % (mountlocation, device))
              return False

        ## Execute mount
	if subprocess.call(['mount', "-L" , disklbl, mountlocation]) != 0:
		logger.error("Unable to mount the ISO image")
		cleanup()
		exit(1)

def umount_device():
	## We do not check the return value, just fails silenty
	subprocess.call(['umount', mountlocation])


def create_tmpdir():
	# creazione della directory temporanea
	# /mnt/tmp/update*

	global tmpdir
	if os.path.exists("%s/tmp"%mountlocation) ==False:
		try:
			os.mkdir("%s/tmp"%mountlocation)
		except e:
			logger.error("Error creating temp dir: %s"%e[1] )
			cleanup()
			exit(1)


	try:
		tmpdir = mkdtemp(prefix='update', dir="%s/tmp" %mountlocation)
	except e:
		logger.error("Unable to create temp dir: %s" % e[1] )
		cleanup()
		exit(1)

def ckrelease():
	# confronto tra la versione sul server e versione installata
	try:
		conf = ConfigParser.RawConfigParser()
		conf.read("%s/%s"%(tmpdir, releasename))
	except e:
		logger.error("Error reading conf file %s" %e[1])
		cleanup()
		exit(1)

	try:
		conf_old=ConfigParser.RawConfigParser()
		conf_old.read(localrelease)
	except e:
		logger.error("Error reading conf file %s" %e[1])
		cleanup()
		exit(1)
	
	try:
		if (conf.getint("gtc","release")<=conf_old.getint("gtc","release")):
			logger.error("You are running an up-to-date verson!")
			logger.error("Be happy!")
			exit(0)
	except  ConfigParser.Error e:
		logger.error("Error reading config %s" %e[1])
		exit(1)

	logger.debug("Your release is old. Go on.")

def ckrelease():
	# confronto tra la versione sul server e versione installata
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
			logger.error("You are running an up-to-date verson!")
			logger.error("Be happy!")
			exit(1)
	except:
		logger.error("Unable to process config %s/%s" % (tmpdir, releasename))
		cleanup()
		exit(1)
	
	logger.debug("Your release is old. Go on.")

def downloadiso():
	# download ISO dal server
	try:
		logger.debug("Attempting to download ISO from %s" % remoteiso )
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
		cleanup()
		exit(1)
	finally:
		logger.debug("Download completed")


		
def cksumiso():
	# controllo tramite sha1 dell'iso che il file non sia corrotto
	try: 
		logger.debug("Check sha1 iso")
		isohash = hashlib.sha1(open("%s/%s"%(tmpdir, isoname), "rb").read()).hexdigest()
	except e:
		logger.error("Error calculating checksum: %s" %e[1])
		cleanup()
		exit(1)
	
	try:
		conf = ConfigParser.RawConfigParser()
		conf.read("%s/%s"%(tmpdir, releasename))
	except e:
                logger.error("Error reading config %s" %e[1])
		cleanup()
		exit(1)
	
	try:
		if (conf.get("gtc","sha1") != isohash):
			logger.error("Error downloading iso, corrupted.")
			cleanup()
			exit(1)
	except e:
                logger.error("Error reading config %s" %e[1])
		cleanup()
		exit(1)
	
	logger.debug("ckiso OK")
	
def replace_iso():
	# sovrascrivo l'iso con la nuova versione.
	logger.debug("Replacing existing installation")
	
	try:	
		if subprocess.call(['mv', "%s/%s"%(tmpdir, isoname),  "%s/%s"% (mountlocation,isoname)]) != 0:
			logger.error("Unable to replace the conf file")
			cleanup()
			exit(1)
		
		if subprocess.call(['mv', "%s/%s"%(tmpdir, releasename), localrelease ]) != 0:
			logger.error("Unable to replace the conf file")
			cleanup()
			exit(1)
	except e:
                logger.error("Error moving file  %s" %e[1])
		cleanup()
		exit(1)

		
	logger.debug("Replaced.")



if __name__ == '__main__':

	## Setup logging first
	logfmt = " %(levelname)s: %(message)s"
	logging.basicConfig(format=logfmt, level=logging.DEBUG)
	logger = logging.getLogger("gtc-updater")

	## Loading config
	getconf()

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
	
	cleanup()	
	
	umount_device()	
	logger.info("All done.")
	logger.info("Please reboot ASAP!")



