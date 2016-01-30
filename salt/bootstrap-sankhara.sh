#!/bin/bash

# Before this script is run, make sure to configure the following:
#  * A user 'infra' exists
#  * The 'kninfra' repository is cloned into /vagrant, and owned by the user infra.
#
# You can do this with the following commands (as root):
#    adduser infra
#    git clone https://github.com/karpenoktem/kninfra.git /vagrant
#    chown -R infra:infra /vagrant
#
# Then run this script.

# Fail on errors.
set -e

# Make sure "sankhara" is in the hostname (needed for salt).
if [[ "`hostname`" != *"sankhara"* ]]; then
    echo "This host (`hostname`) doesn't have sankhara in it's name, abort."
    exit 1
fi

# Make sure salt-minion is installed.
if [ ! -e /usr/bin/salt-minion ]; then
    apt update
    apt install salt-minion
fi

# Set salt-minion to masterless mode.
sed -i "s/#?file_client: .*$/file_client: local/" /etc/salt/minion
# Don't run the minion daemon, we're going to use salt-call.
systemctl stop salt-minion
systemctl disable salt-minion
# Some black magic to set the right file_roots:
sed -i "s/^#file_roots:$/file_roots:/" /etc/salt/minion
sed -i "/^file_roots:$/{n;s/.*/  base:/;n;s/.*/    - \/vagrant\/salt\/states/}" /etc/salt/minion
# And again for pillar_roots:
sed -i "s/^#pillar_roots:$/pillar_roots:/" /etc/salt/minion
sed -i "/^pillar_roots:$/{n;s/.*/  base:/;n;s/.*/    - \/vagrant\/salt\/pillar/}" /etc/salt/minion

# add the vagrant grain
if ! egrep -q "^grains:$" /etc/salt/minion; then
    # I've had enough of sed
    cat << EOF >> /etc/salt/minion

# Added by bootstrap script
grains:
  vagrant: true
EOF
fi

if [ ! -e /vagrant/salt/pillar/vagrant.sls ]; then
    python /vagrant/salt/states/sankhara/vagrant-sls.py > /vagrant/salt/pillar/vagrant.sls
fi

if [ ! -d /home/vagrant ]; then
    adduser vagrant
fi

# ... aaaand run!
salt-call --local state.highstate
