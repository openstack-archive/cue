#!/bin/bash
set -x
unset UCF_FORCE_CONFFOLD
export UCF_FORCE_CONFFNEW=YES
ucf --purge /boot/grub/menu.lst
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -o Dpkg::Options::="--force-confnew" --force-yes -fuy dist-upgrade
sudo apt-get -y install git
cd /home/ubuntu/
sudo -u ubuntu git clone https://git.openstack.org/openstack-dev/devstack
cat > devstack/local.conf<< EOF
[[local|localrc]]
HOST_IP=127.0.0.1
REQUIREMENTS_MODE=soft
ADMIN_PASSWORD=password
MYSQL_PASSWORD=password
RABBIT_PASSWORD=password
SERVICE_PASSWORD=password
SERVICE_TOKEN=password
LOGFILE=/opt/stack/logs/stack.sh.log
VERBOSE=True
LOG_COLOR=True
SCREEN_LOGDIR=/opt/stack/logs
disable_service g-api
disable_service g-reg
disable_service n-api
disable_service n-crt
disable_service n-obj
disable_service n-cpu
disable_service n-net
disable_service n-cond
disable_service n-sch
disable_service n-novnc
disable_service n-xvnc
disable_service n-cauth
disable_service c-sch
disable_service c-api
disable_service c-vol
disable_service h-eng
disable_service h-api
disable_service h-api-cfn
disable_service h-api-cw
disable_service horizon
disable_service tempest
EOF
sudo -u ubuntu ./devstack/stack.sh
