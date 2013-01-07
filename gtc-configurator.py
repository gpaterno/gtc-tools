#!/usr/bin/env python
##
## GTC Configuration tool
## This automatically configures wireless and desktop links
##
import os
import uuid
import subprocess
import gpgme
import StringIO

def setup_wireless(wireless):
	
	try:
		essid=wireless.get("essid")
		wtype = wireless.get("type")

		if wtype == "wpa/psk":
			psk=wireless.get("psk")
		elif wtype == "open":
			psk=""
		else:
			logger.error("unknown type")
			return False
	except:
		logger.error("reading configuration")
		return False

	

	try:
		filename="/etc/NetworkManager/system-connections/%s" % essid
		fh = open(filename, "w")
		fh.write("[connection]\n")
		fh.write("id=%s (GTC)\n"%essid)
		fh.write("uuid=%s\n" % uuid.uuid1())
		fh.write("type=802-11-wireless\n\n")
		fh.write("[802-11-wireless]\n")
		fh.write("mode=infrastructure\n")
		fh.write("ssid=%s\n" %essid)
		fh.write("security=802-11-wireless-security\n\n")
		fh.write("[802-11-wireless-security]\n")
		fh.write("key-mgmt=wpa-psk\n") 
		fh.write("psk=%s\n" %psk)
		fh.close()
		os.chmod(filename,0600)
	except:
		logger.error("Error writing wireless confinguration")
		return False
	finally:
		logger.info("Connection \"%s (GTC)\" configured"%essid)
	return True

	

def setup_vmware(wmware):
	pass

if __name__ == "__main__":
	import json
	import logging
	
	## Setup logging first
	logfmt = " %(levelname)s: %(message)s"
	logging.basicConfig(format=logfmt, level=logging.DEBUG)
	global logger
	logger = logging.getLogger("gtc-updater")

	conf = ""
	conffiles  = ['/isodevice/gtc/gtc.conf.gpg', os.getcwd() + '/gtc.conf.gpg']
	conf_found = 0

	## Get Config File
	for tconf in conffiles:
		if os.path.isfile(tconf):
			conf   = tconf
			conf_found = 1

	if conf_found == 0:
		logger.debug("Unable to find configuration files")
		exit (0)


	
	try:
		signature = StringIO.StringIO(open(conf,"r").read() )
		plaintext = StringIO.StringIO()
		#os.environ['GNUPGHOME'] = '/etc/gtc/keys'
		os.environ['GNUPGHOME'] = '/home/alorenzi/tmp'

		ctx = gpgme.Context()
		sigs = ctx.verify(signature, None, plaintext)

		if len(sigs) > 0:
			if sigs[0].status!=None:
				logger.error("GPG sign not valid")
				exit(1)

			conf = json.loads( plaintext.getvalue() )

			
		else:
			logger.error ("GPG sign not valid")
			exit (1)
		
	except:
		logger.error("Error loading json")
		exit(1)



	if conf.get("wireless") != None:
		
		while len(conf.get("wireless"))>0:
			setup_wireless( conf.get("wireless").pop())

	else:
		logger.info("No wireless in conf file")

	if conf.get("vmware") != None:
		while len(  conf.get("vmware")) >0:
			setup_vmware(conf.get("vmware").pop())
	else:
		logger.info("No vmware in conf file")

	exit (0)
