# Devstack init script
$devstack_script = <<SCRIPT
#!/bin/bash
set -e

DEBIAN_FRONTEND=noninteractive sudo apt-get -qqy update || sudo yum update -qy
DEBIAN_FRONTEND=noninteractive sudo apt-get install -qqy git || sudo yum install -qy git
pushd ~

# Copy over git config
cat << EOF > /home/vagrant/.gitconfig
#{GITCONFIG}
EOF

test -d devstack || git clone https://git.openstack.org/openstack-dev/devstack

rsync -av --exclude='.tox' --exclude='.venv' --exclude='.vagrant' --exclude='contrib/vagrant' /home/vagrant/cue /opt/stack

if [ -f "/home/vagrant/python-cueclient" ]; then
    rsync -av --exclude='.tox' --exclude='.venv' --exclude='.vagrant' --exclude='contrib/vagrant' /home/vagrant/python-cueclient /opt/stack
fi

# Install Vagrant local.conf sample
if [ ! -f "/home/vagrant/devstack/local.conf" ]; then
    cp /opt/stack/cue/contrib/devstack/local.conf /home/vagrant/devstack/local.conf
fi

for f in extras.d/* lib/*; do
    if [ ! -f "/home/vagrant/devstack/$f" ]; then
        ln -fs /opt/stack/cue/contrib/devstack/$f -t /home/vagrant/devstack/$(dirname $f)
    fi
done

SCRIPT

