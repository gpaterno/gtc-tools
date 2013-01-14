#!/usr/bin/env python
##
## GTC Configuration tool
## ====================
##
## This automatically configures wireless and desktop links for vmware
## Takes settings from a json file signed with PGP.
##

import os
import uuid
import subprocess
import gpgme
import StringIO
import re

def setup_wireless(wireless):
	# method to configure wireless. Accept an argument,
	# a dictionary [essid, type, psk]
	# at the moment this accept only open or wpa/psk wireless.
	
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
		# Writing Network Manager conf
		
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

	

def setup_vmware(vmware):
	# method to configure vmware links in left bar. Accept an argument,
	# a dictionary [id, server, icon]
	# at the moment this accept only open or wpa/psk wireless.
	
	from base64 import b64decode


	try:
		ident=vmware.get("id")
		server = vmware.get("server")
		icon =  vmware.get("icon")
		
	except:
		logger.error("reading configuration")
		return False

	try:
		# vmware["icon"] is a png encoded in base64.
		# We have to decode and save it in an image.
		iconpath= "/usr/share/pixmaps/vmware-%s.png" % ident
		fh=open(iconpath ,"w")
		fh.write(b64decode(icon))
		fh.close()
	except:
		logger.error("Creating icon")
		return False	

	# making desktop file
	logger.info("start making launcher")
	desktop_content =  "[Desktop Entry] \n"
	desktop_content += "Name=connect virtual machine %s \n" %server
	desktop_content += "Comment= \n"
	desktop_content += "Exec=/usr/bin/vmware-view -s %s \n" %server
	desktop_content += "Icon=%s\n" %iconpath
	desktop_content += "Type=Application\n"
	desktop_content += "StartupNotify=true"
	
	try:
		desktop_file=open("/usr/share/applications/vmware-%s.desktop" % ident ,"w")
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
				yetexists =  re.search("'vmware-%s.desktop'" % ident, line)
				# modify line "favorites" if vmware-*.desktop not exists 
				if fav!= None and yetexists == None:
					line = re.sub("]", ", 'vmware-%s.desktop']" % ident ,line)
				newcontent+=line
		gschema_file.close()

		# writing new gtc.gschema.override
		gschema_file=open("/usr/share/glib-2.0/schemas/gtc.gschema.override", "w")
		gschema_file.write(newcontent)
		gschema_file.close()
	except:
		logger.error("ERROR while writing gtc.gschema.override")
		return False
		
	logger.info("Created vmware configuration")	



if __name__ == "__main__":
	# STARTS HERE
	import json
	import logging
	
	## Setup logging first
	logfmt = " %(levelname)s: %(message)s"
	logging.basicConfig(format=logfmt, level=logging.DEBUG)
	global logger
	logger = logging.getLogger("gtc-updater")

	# Get Config File
	conf = ""
	conffiles  = ['/isodevice/gtc/gtc.conf.gpg', os.getcwd() + '/gtc.conf.gpg']
	conf_found = 0

	for tconf in conffiles:
		if os.path.isfile(tconf):
			conf   = tconf
			conf_found = 1

	if conf_found == 0:
		logger.debug("Unable to find configuration files")
		exit (0)


	# verify PGP signature. 
	try:
		signature = StringIO.StringIO(open(conf,"r").read() )
		plaintext = StringIO.StringIO()
		os.environ['GNUPGHOME'] = '/etc/gtc/keys'

		ctx = gpgme.Context()
		sigs = ctx.verify(signature, None, plaintext)

		if len(sigs) > 0:
			if sigs[0].status!=None:
				logger.error("GPG sign not valid")
				#exit(1)

			conf = json.loads( plaintext.getvalue() )

			
		else:
			logger.error ("GPG sign not valid")
			exit (1)
		
	except:
		logger.error("Error loading json")
		exit(1)


	# takes wireless config and call setup_wireless
	if conf.get("wireless") != None:
		
		while len(conf.get("wireless"))>0:
			setup_wireless( conf.get("wireless").pop())

	else:
		logger.info("No wireless in conf file")

	# takes vmware config and call setup_vmware
	if conf.get("vmware") != None:
		while len(  conf.get("vmware")) >0:
			setup_vmware(conf.get("vmware").pop())
	else:
		logger.info("No vmware in conf file")


	exit (0)
