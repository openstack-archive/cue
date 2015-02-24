#!/bin/bash

TOP_DIR=$(cd $(dirname "$0") && pwd)
source $TOP_DIR/functions
source $TOP_DIR/stackrc
source $TOP_DIR/lib/cue
DEST=${DEST:-/opt/stack}

source $TOP_DIR/openrc admin admin

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
fi

if [[ -z $CUE_MANAGEMENT_KEY ]]; then
    CUE_MANAGEMENT_KEY='vagrant'
fi

# Add ssh keypair to admin account
if [[ -z $(nova keypair-list | grep vagrant) ]]; then
    nova keypair-add --pub-key ~/.ssh/id_rsa.pub vagrant
fi

# Add ping and ssh rules to rabbitmq security group
neutron security-group-rule-create --direction ingress --protocol icmp --remote-ip-prefix 0.0.0.0/0 $CUE_RABBIT_SECURITY_GROUP
neutron security-group-rule-create --direction ingress --protocol tcp --port-range-min 22 --port-range-max 22 --remote-ip-prefix 0.0.0.0/0 $CUE_RABBIT_SECURITY_GROUP

# Add static nameserver to private-subnet
neutron subnet-update --dns-nameserver 8.8.8.8 private-subnet

# Add ssh keypair to demo account
source $TOP_DIR/openrc demo demo
if [[ -z $(nova keypair-list | grep $CUE_MANAGEMENT_KEY) ]]; then
    nova keypair-add --pub-key ~/.ssh/id_rsa.pub $CUE_MANAGEMENT_KEY
fi

