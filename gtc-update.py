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
from ctypes import *

MS_REMOUNT = 32
MS_RDONLY  = 1
LINUX_LIBC = "libc.so.6"
MOUNTPOINT = "/cdrom"
BASEURL    = "http://www.pontiradio.org/gtc/"
ISOFILE	   = "gippa.iso"
TMPDIR     = "/cdrom/$$tmpdir"
LOGFMT     = "%(levelname)s: %(message)s"


## Download progress
def iso_progress(download_t, download_d, upload_t, upload_d):
	if float(download_t) != 0:
	    percentage = float(download_d)*100/float(download_t)
	    print "Downloading: %s%% \r" % int(percentage),


if __name__ == '__main__':

	## Logging
	logging.basicConfig(format=LOGFMT, level=logging.DEBUG)
	logger = logging.getLogger("gtc-updater")

        ## Load the libc to call mount
	libc = cdll.LoadLibrary(LINUX_LIBC)

	## Let's remount the filesystem in read-write
	if libc.mount(None, "/cdrom", None, MS_REMOUNT, None) != 0:
		print "Cannot remount filesystem in read-write, mount operation failed"
		exit(1)

	# Check if the filesystem is in read-write
	# mount operation returns 0 also if it's on a CD, so let's check
	# if we are in read-write
	if os.statvfs("/cdrom")[8] & MS_RDONLY:
		print "You're running from a CD (or we're having problem mounting)"
		exit(1)

        ## 
	## PLACEHOLDER: download RELEASE file and check
	## it's newer
	##

        ## Removing if temp dir exists 
	if os.path.exists(TMPDIR):
		logger.debug("Removing %s as it exists" % TMPDIR)
		shutil.rmtree(TMPDIR)

        ## (Re)create a temp dir for downloading ISO
	logger.debug("Creating temp dir %s" % TMPDIR)
	os.makedirs(TMPDIR)

        ## Download the ISO
	logger.debug("Attempting to download from %s/%s" % (BASEURL, "/gippa.iso"))
	filename = "%s/%s" % (TMPDIR, ISOFILE)
	iso = open(filename, "wb")
	dwnld = pycurl.Curl()
        dwnld.setopt(pycurl.URL, BASEURL + ISOFILE)
	dwnld.setopt(pycurl.NOPROGRESS, 0)
        dwnld.setopt(pycurl.PROGRESSFUNCTION, iso_progress)
	dwnld.setopt(pycurl.WRITEDATA, iso)
	dwnld.perform()
	dwnld.close()
	iso.close()

	## Reset the filesystem in read-only
	if libc.mount(None, "/cdrom", None, MS_REMOUNT+MS_RDONLY, None) != 0:
		print "Cannot remount filesystem in read-only, mount operation failed"
		exit(1)
