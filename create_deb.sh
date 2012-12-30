#!/bin/sh -x
mkdir -p debianpkg/usr/sbin/ debianpkg/etc/init debianpkg/etc/gtc debianpkg/DEBIAN/ debianpkg/usr/share/gtc

cp control debianpkg/DEBIAN/
cp gtc-configurator.py debianpkg/usr/sbin/gtc-configurator
cp gtc-update.py debianpkg/usr/sbin/gtc-update
cp gtc-install debianpkg/usr/sbin/gtc-install 
chmod +x debianpkg/usr/sbin/*


cp garl_little.png debianpkg/usr/share/gtc
dpkg -b debianpkg gtc-tools.deb
