# Rally init script
$rally_script = <<SCRIPT
#!/bin/bash
set -e

DEBIAN_FRONTEND=noninteractive sudo apt-get -qqy update || sudo yum update -qy
DEBIAN_FRONTEND=noninteractive sudo apt-get install -qqy git || sudo yum install -qy git
pushd ~

test -d devstack || git clone https://git.openstack.org/openstack-dev/devstack
test -d rally || git clone https://github.com/openstack/rally
cp rally/contrib/devstack/lib/rally devstack/lib/
cp rally/contrib/devstack/extras.d/70-rally.sh devstack/extras.d/
cd devstack
echo "enable_service rally" >> local.conf

SCRIPT
