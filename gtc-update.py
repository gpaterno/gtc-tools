#!/usr/bin/python
#
# GTC Updater
# (c) 2012 Giuseppe "Gippa" Paterno' (gpaterno@gpaterno.com)
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

MS_REMOUNT = 32
MS_RDONLY  = 1
LINUX_LIBC = "libc.so.6"
MOUNTPOINT = "/cdrom"
BASEURL    = "http://172.16.212.1/~gpaterno/"
ISOFILE    = "gippa.iso"
TMPDIR     = "/cdrom/$$tmpdir/"
LOGFMT     = "%(levelname)s: %(message)s"


def cdrom_image(mount=True):
	imagedir = '/upgrade'

	# Do we have to mount?
	if mount:
		## check if it's not already mounted
		if os.path.isdir(imagedir + "/casper"):
			logger.warning("ISO image is aready mounted, calling dismount")
			cdrom_image(mount=False)

		# Delete mount point if exists
        	if os.path.exists(imagedir):
                	logger.debug("Removing %s and subdir as it exists" % imagedir)
                	shutil.rmtree(imagedir)

        	## (Re)create mount point
        	logger.debug("Creating mountpoint %s" % imagedir)
        	os.makedirs(imagedir)

		## Mount the image
		logger.debug("Mounting the ISO image")
 		if subprocess.call(['mount', '-o', 'loop,ro', '/cdrom/$$tmpdir/gippa.iso', imagedir]) != 0:
			logger.error("Unable to mount the ISO image")
			exit(1)

		## Placeholder, check for files we expect

	# Else dismount
	else:
		## Dismount
		logger.debug("Dismounting ISO image")
		if subprocess.call(['umount', imagedir]) != 0:
			logger.error("Unable to umount the ISO image")
			exit(1)

## Download progress
def iso_progress(download_t, download_d, upload_t, upload_d):
	if float(download_t) != 0:
	    percentage = float(download_d)*100/float(download_t)
	    print "Downloading: %s%% \r" % int(percentage),


if __name__ == '__main__':

	## Logging
	logging.basicConfig(format=LOGFMT, level=logging.DEBUG)
	logger = logging.getLogger("gtc-updater")

	## Welcome msg and warning
	logger.info("Checking for upgrades, make sure you're connected to the network and you have your power adapter connected.")

        ## Load the libc to call mount
	libc = cdll.LoadLibrary(LINUX_LIBC)

	## Let's remount the filesystem in read-write
	logger.debug("Remounting RW /cdrom")
	if libc.mount(None, "/cdrom", None, MS_REMOUNT, None) != 0:
		logger.error("Cannot remount filesystem in read-write, mount operation failed")
		exit(1)

	# Check if the filesystem is in read-write
	# mount operation returns 0 also if it's on a CD, so let's check
	# if we are in read-write
	logger.debug("Check if /cdrom is really in RW")
	if (int(os.statvfs("/cdrom")[8]) % 2) != 0:
		logger.error("You're running from a CD (or we're having problem mounting)")
		exit(1)

        ## Removing if temp dir exists 
	if os.path.exists(TMPDIR):
		logger.debug("Removing %s and subdir as it exists" % TMPDIR)
		shutil.rmtree(TMPDIR)

        ## (Re)create a temp dir for downloading ISO
	logger.debug("Creating temp dir %s" % TMPDIR)
	os.makedirs(TMPDIR)

        ## Download the ISO
	try:
		logger.debug("Attempting to download from %s/%s to %s/%s" % (BASEURL, ISOFILE, TMPDIR, ISOFILE))
		iso = open(TMPDIR + "/gippa.iso", "wb")
		dwnld = pycurl.Curl()
        	dwnld.setopt(pycurl.URL, BASEURL + ISOFILE)
		dwnld.setopt(pycurl.NOPROGRESS, 0)
        	dwnld.setopt(pycurl.PROGRESSFUNCTION, iso_progress)
		dwnld.setopt(pycurl.WRITEDATA, iso)
		dwnld.perform()
	except pycurl.error, e:
		logger.error("Download failed: %s" % e[1])
	finally:
		print ""        # print empty line
		dwnld.close()
		iso.close()

	## Calculate and check the sha1sum of the image
        isohash = hashlib.sha1(open(TMPDIR + "/" + ISOFILE, "rb").read()).hexdigest()
        print "ISO hash is: %s" % isohash

	## Placeholder, check that hash is OK

	## Mount ISO image
	cdrom_image(mount=True)

	## Copying over the casper
	logger.warning("Copying the image, DO NOT power off")

	## Dismount ISO image
	cdrom_image(mount=False)

	## Flushing filesystem before turning read-only
	logger.debug("Syncing filesystems")
	libc.sync()

	## Reset the filesystem in read-only
	logger.debug("Remount /cdrom in RO")
	if libc.mount(None, "/cdrom", None, MS_REMOUNT+MS_RDONLY, None) != 0:
		logger.error("Cannot remount filesystem in read-only, mount operation failed")
		exit(1)
