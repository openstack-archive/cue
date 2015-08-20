# Rally init script
$rally_script = <<SCRIPT
#!/bin/bash
set -e

DEBIAN_FRONTEND=noninteractive sudo apt-get -qqy update || sudo yum update -qy
DEBIAN_FRONTEND=noninteractive sudo apt-get install -qqy git || sudo yum install -qy git
pushd ~

test -d devstack || git clone https://git.openstack.org/openstack-dev/devstack
test -d rally || git clone https://github.com/openstack/rally
cd devstack
echo "enable_plugin rally https://github.com/openstack/rally master" >> localrc

cat << EOF >> /home/vagrant/.bash_aliases
alias run_rally_cue_scenarios="rally -v --debug task start --task ~/cue/rally-jobs/rabbitmq-scenarios.yaml"

EOF

SCRIPT
