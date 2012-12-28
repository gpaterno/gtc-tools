#!/usr/bin/env python
def setup_wireless(wireless):
	import os
	import uuid
	
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

	conf = "./gtc.conf"
	try:
		conf = json.load(open(conf))
	except:
		logger.ERROR("Error loading json")
		exit(0)

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
