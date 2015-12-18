#!/bin/bash

set -o xtrace

TOP_DIR=$(cd $(dirname "$0") && pwd)
source $TOP_DIR/functions
source $TOP_DIR/stackrc
source $TOP_DIR/lib/cue
DEST=${DEST:-/opt/stack}

IDENTITY_API_VERSION=3 source $TOP_DIR/openrc admin admin

IPTABLES_RULE='iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE'

# Create NAT rule to allow VMs to NAT to host IP
if [[ -z $(sudo iptables -t nat -L | grep MASQUERADE | tr -d ' ' | grep anywhereanywhere) ]]; then
    sudo $IPTABLES_RULE
fi

# Make VM NAT rule persistent
# TODO(sputnik13): this should ideally be somewhere other than /etc/rc.local
if [[ -z $(grep "$IPTABLES_RULE" /etc/rc.local) ]]; then
    sudo sed -i -e "s/^exit 0/$IPTABLES_RULE\nexit 0/" /etc/rc.local
fi

if [[ ! -x /etc/rc.local ]]; then
    sudo chmod +x /etc/rc.local
fi

# Generate an ssh keypair to add to devstack
if [[ ! -f ~/.ssh/id_rsa ]]; then
    ssh-keygen -q -t rsa -N "" -f ~/.ssh/id_rsa
    # copying key to /tmp so that tests can access it
    cp ~/.ssh/id_rsa /tmp/cue-mgmt-key
    chmod 644 /tmp/cue-mgmt-key
fi

if [[ -z $CUE_MANAGEMENT_KEY ]]; then
    CUE_MANAGEMENT_KEY='vagrant'
fi

# Add ssh keypair to admin account
if [[ -z $(openstack keypair list | grep $CUE_MANAGEMENT_KEY) ]]; then
    openstack keypair create --public-key ~/.ssh/id_rsa.pub $CUE_MANAGEMENT_KEY
fi

# Add ping and ssh rules to rabbitmq security group
neutron security-group-rule-create --direction ingress --protocol icmp --remote-ip-prefix 0.0.0.0/0 $CUE_RABBIT_SECURITY_GROUP
neutron security-group-rule-create --direction ingress --protocol tcp --port-range-min 22 --port-range-max 22 --remote-ip-prefix 0.0.0.0/0 $CUE_RABBIT_SECURITY_GROUP

# Add static nameserver to private-subnet
neutron subnet-update --dns-nameserver 8.8.8.8 private-subnet

unset OS_PROJECT_DOMAIN_ID
unset OS_REGION_NAME
unset OS_USER_DOMAIN_ID
unset OS_IDENTITY_API_VERSION
unset OS_PASSWORD
unset OS_AUTH_URL
unset OS_USERNAME
unset OS_PROJECT_NAME
unset OS_TENANT_NAME
unset OS_VOLUME_API_VERSION
unset COMPUTE_API_VERSION
unset OS_NO_CACHE

# Add ssh keypair to demo account
IDENTITY_API_VERSION=3 source $TOP_DIR/openrc demo demo
if [[ -z $(openstack keypair list | grep $CUE_MANAGEMENT_KEY) ]]; then
    openstack keypair create --public-key ~/.ssh/id_rsa.pub $CUE_MANAGEMENT_KEY
fi

