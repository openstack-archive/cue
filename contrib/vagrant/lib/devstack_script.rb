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

test -d /home/vagrant/bin || mkdir /home/vagrant/bin

cat << EOF > /home/vagrant/bin/refresh_devstack.sh
#!/bin/bash
rsync -av --exclude='.tox' --exclude='.venv' --exclude='.vagrant' /home/vagrant/cue /opt/stack

if [ -d "/home/vagrant/python-cueclient" ]; then
    rsync -av --exclude='.tox' --exclude='.venv' --exclude='.vagrant' --exclude='contrib/vagrant' /home/vagrant/python-cueclient /opt/stack
fi

if [ -d "/home/vagrant/cue-dashboard" ]; then
    rsync -av --exclude='.tox' --exclude='.venv' --exclude='.vagrant' --exclude='contrib/vagrant' /home/vagrant/cue-dashboard /opt/stack
fi

# Install Vagrant local.conf sample
if [ ! -f "/home/vagrant/devstack/local.conf" ]; then
    cp /opt/stack/cue/contrib/devstack/local.conf /home/vagrant/devstack/local.conf
fi

# Install Vagrant local.sh sample
if [ ! -f "/home/vagrant/devstack/local.sh" ]; then
    cp /opt/stack/cue/contrib/devstack/local.sh /home/vagrant/devstack/local.sh
fi

pushd /home/vagrant/cue/contrib/devstack
for f in extras.d/* lib/*; do
    if [ ! -f "/home/vagrant/devstack/\\$f" ]; then
        ln -fs /opt/stack/cue/contrib/devstack/\\$f -t /home/vagrant/devstack/\\$(dirname \\$f)
    fi
done
popd
EOF

chmod +x /home/vagrant/bin/refresh_devstack.sh

cat << EOF >> /home/vagrant/.bash_aliases
alias refresh_devstack="/home/vagrant/bin/refresh_devstack.sh"

EOF

/home/vagrant/bin/refresh_devstack.sh

SCRIPT

