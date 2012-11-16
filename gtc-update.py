#!/usr/bin/python
#
# GTC Updater
# (c) 2012 Giuseppe "Gippa" Paterno' (gpaterno@gpaterno.com)
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
from ctypes import *

MS_REMOUNT = 32
MS_RDONLY  = 1
LINUX_LIBC = "libc.so.6"
MOUNTPOINT = "/cdrom"

if __name__ == '__main__':
	libc = cdll.LoadLibrary(LINUX_LIBC)

	## Let's remount the filesystem in read-write
	if libc.mount(None, "/cdrom", MS_REMOUNT, None) != 0:
		print "Cannot remount filesystem in read-write, mount operation failed"
		exit(1)

	# Check if the filesystem is in read-write
	# mount operation returns 0 also if it's on a CD, so let's check
	# if we are in read-write
	if os.statvfs("/cdrom")[8] & MS_RDONLY:
		print "You're running from a CD (or we're having problem mounting)"
		exit(1)


	## Reset the filesystem in read-only
	if libc.mount(None, "/cdrom", MS_REMOUNT = MS_RDONLY, None) != 0:
		print "Cannot remount filesystem in read-only, mount operation failed"
		exit(1)
