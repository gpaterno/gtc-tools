#!/bin/sh -x

mkdir -p debianpkg/DEBIAN/
mkdir -p debianpkg/usr/sbin/
mkdir -p debianpkg/etc/init
mkdir -p debianpkg/etc/gtc
mkdir -p debianpkg/usr/share/gtc
mkdir -p debianpkg/usr/share/applications
mkdir -p debianpkg/usr/share/pixmaps
mkdir -p debianpkg/usr/share/glib-2.0/schemas/
mkdir -p debianpkg/etc/skel/.vmware/
mkdir -p debianpkg/etc/gtc/keys

cp control debianpkg/DEBIAN/

cp gtc-configurator.py debianpkg/usr/sbin/gtc-configurator
cp gtc-update.py debianpkg/usr/sbin/gtc-update
cp qt-gtc-update.py debianpkg/usr/sbin/qt-gtc-update
cp gtc-install debianpkg/usr/sbin/gtc-install 
chmod +x debianpkg/usr/sbin/*

cp global.ini debianpkg/etc/gtc
cp gtc.conf debianpkg/etc/gtc
cp gtc.conf.sign debianpkg/etc/gtc

cp app/*.desktop debianpkg/usr/share/applications
cp app/*.png debianpkg/usr/share/pixmaps

cp gtc.gschema.override /usr/share/glib-2.0/schemas/

cp vmware/vmware-view-client.license-accepted debianpkg/etc/skel/.vmware-view-client.license-accepted
cp vmware/view-preferences debianpkg/etc/skel/.vmware/view-preferences

cp keys/pubring.gpg* debianpkg/etc/gtc/keys

cp init/* debianpkg/etc/init

dpkg -b debianpkg gtc-tools.deb
