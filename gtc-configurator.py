#!/usr/bin/env python
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
		fh = open("/etc/NetworkManager/system-connections/%s" % essid, "w")
		fh.write("[connection]\n")
		fh.write("id=\"%s (GTC)\"\n"%essid)
		fh.write("ssid=\"%s\"\n" %essid)
		fh.write("key-mamt=wpa-psk\n") 
		fh.write("psk=%s\n" %psk)
		fh.close()
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
