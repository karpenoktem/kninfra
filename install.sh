#!/bin/bash

# This script installs and configures everything required to run kninfra inside a virtual machine.
#
# First, prepare a bare-bones Debian installation. Example configuration:
#   * 384MB RAM
#   * 8GB hard disk
#   * Debian Wheezy with just the 'SSH Server' and 'Standard system utilities' selected during installation and git installed
#
# Extra VirtualBox configuration to SSH into the guest:
#   * Add one host-only adapter inside VirtualBox (File>Preferences>Network).
#   * Add that adapter to the guest like this:
#     https://muffinresearch.co.uk/howto-ssh-into-virtualbox-3-linux-guests/
#
# Then:
#   * make sure root can ssh to khandhas (edit /root/.ssh/config to enable this)
#   * add the user 'infra'
#   * clone kninfra to /home/infra/repo
#   * run this script as root from that repo
#
# After the script has run, edit line 22 of /etc/lighttpd/rewrites.conf:
#     $HTTP["host"] =~ "^(?:(www|khandhas|dev|nibbana)\.)?(karpenoktem.(nl|com)|kn.cx)$" {
# Change the hostname (the part between ^ and $) to the hostname your guest can be reached at from the host.
#
# To start the server, run as user infra:
#     PYTHONPATH=/home/infra/py /home/infra/repo/bin/run-fcgi
# This starts the Django server.

# exit on errors
set -e

# temporary files directory
tmpdir="/tmp/kninfra-$$"
mkdir $tmpdir



echo '*** installing required packages...'
apt-get install lighttpd php5-cgi python-django msgpack-python python-setuptools python-pyparsing python-markdown python-flup python-pymongo python-mysqldb python-imaging mongodb mailman

mkdir -p /home/infra/scm
mkdir -p /home/infra/py

if [ ! -d /home/infra/scm/mirte ]; then
	git clone https://github.com/bwesterb/mirte.git /home/infra/scm/mirte
fi

if [ ! -f /usr/local/bin/mirte ]; then
	(cd /home/infra/scm/mirte; python setup.py install)
fi

if [ ! -d /home/infra/scm/koert ]; then
	git clone https://github.com/awesterb/koert.git /home/infra/scm/koert
fi

if [ ! -d /home/infra/scm/regl ]; then
	git clone https://github.com/karpenoktem/regl.git /home/infra/scm/regl
fi

ln -sf ../scm/koert /home/infra/py/koert
ln -sf ../scm/regl  /home/infra/py/regl





echo -e '\n*** configuring users and groups...'
if ! grep -Eq '^interinfra:' /etc/group; then
	addgroup interinfra
fi
if ! grep -Eq '^interinfra:.*:.*:.*\bwww-data\b' /etc/group; then
	adduser www-data interinfra
fi
if ! grep -Eq '^interinfra:.*:.*:.*\binfra\b' /etc/group; then
	adduser infra interinfra
fi





echo -e '\n*** configuring kninfra...'
mkdir -p /home/infra/media
ln -fs ../repo/kn/base/media/        /home/infra/media/base
ln -fs ../repo/kn/leden/media/       /home/infra/media/leden
ln -fs ../repo/kn/reglementen/media/ /home/infra/media/reglementen
ln -fs ../repo/kn/static/media/      /home/infra/media/static
mkdir -p /home/infra/storage
ln -fs ../media/ /home/infra/storage/media

# this appear to be the default location in Debian
if [ ! -f /var/lib/mongodb/kn.0 ]; then
	# copy the whole database from khandhas
	ssh khandhas mongodump --db kn
	scp -r khandhas:dump/kn $tmpdir/mongodb-dump
	mongorestore --db kn --dir $tmpdir/mongodb-dump
fi
if [ ! -f /home/infra/repo/kn/settings.py ]; then
	cp /home/infra/repo/kn/settings.example.py /home/infra/repo/kn/settings.py
fi




echo -e '\n*** configuring lighttpd...'
mkdir -p /srv/default
sed -i 's/# *"mod_rewrite",/\t"mod_rewrite",/g' /etc/lighttpd/lighttpd.conf
sed -i 's:\(server\.document-root.*= "\).*":\1/srv/default":g'    /etc/lighttpd/lighttpd.conf
if [ ! -f /etc/lighttpd/rewrites.conf ]; then
	scp khandhas:/etc/lighttpd/rewrites.conf /etc/lighttpd/rewrites.conf
fi
if ! grep -Fxq 'include "rewrites.conf"' /etc/lighttpd/lighttpd.conf; then
	echo >> /etc/lighttpd/lighttpd.conf
	echo 'include "rewrites.conf"' >> /etc/lighttpd/lighttpd.conf
fi

if [ ! -f /etc/lighttpd/conf-enabled/*-cgi.conf ]; then
	lighttpd-enable-mod cgi
fi

if [ ! -f /etc/lighttpd/conf-enabled/*-fastcgi-php.conf ]; then
	lighttpd-enable-mod fastcgi-php
fi

cat >/etc/lighttpd/conf-enabled/15-fastcgi-kninfra.conf <<EOF
fastcgi.server += (
       "/kndjango.fcgi" =>
       ( "localhost" =>
               (       "socket" => "/home/infra/fcgi.sock",
                       "check-local" => "disable",
               )
       )
)
EOF

service lighttpd restart

rm -r $tmpdir
