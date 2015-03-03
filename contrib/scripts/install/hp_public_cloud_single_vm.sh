#!/bin/bash
unset UCF_FORCE_CONFFOLD
export UCF_FORCE_CONFFNEW=YES
ucf --purge /boot/grub/menu.lst
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get -o Dpkg::Options::="--force-confnew" --force-yes -fuy dist-upgrade
apt-get install -y python-pip python-dev git build-essential zookeeper zookeeperd python-mysqldb supervisor
debconf-set-selections <<< 'mysql-server mysql-server/root_password password password'
debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password password'
apt-get -y install mysql-server
yes w | sudo pip install -e git+https://github.com/stackforge/cue#egg=cue
echo "create database cue;" | mysql -u root -ppassword
mkdir -p /etc/cue
cat > /etc/cue/cue.conf << EOF
[DEFAULT]
rabbit_port=5672
auth_strategy=noauth
debug=true
[api]
host_ip=0.0.0.0
port=8795
max_limit=1000
os_image_id=9d25fe2d-cf31-4b05-8c58-f238ec78e633
[database]
connection=mysql://root:password@127.0.0.1/cue
[openstack]
os_key_name=
EOF
cat > /etc/cue/worker.conf << EOF
[database]
connection=mysql://root:password@127.0.0.1/cue
[openstack]
#os_tenant_id=
os_region_name=
os_tenant_name=
os_username=
os_password=
os_auth_url=
EOF
cat > /etc/cue/policy.json<< EOF
{
    "admin": "role:admin or is_admin:True",
    "owner": "tenant:%(tenant_id)s",
    "admin_or_owner": "rule:admin or rule:owner",
    "default": "rule:admin_or_owner",
    "cluster:create": "rule:admin_or_owner",
    "cluster:get": "rule:admin_or_owner",
    "cluster:delete": "rule:admin_or_owner",
    "cluster:update_status": "rule:admin_or_owner",
    "clusters:get": "rule:admin_or_owner"
}
EOF
cue-manage --config-file /etc/cue/cue.conf database upgrade
cue-manage --config-file /etc/cue/worker.conf taskflow upgrade
cat > /etc/supervisor/conf.d/cueapi.conf<< EOF
[program:cue-api]
command=cue-api --debug --config-file /etc/cue/cue.conf
process_name=%(program_name)s
stdout_logfile=/var/log/cue-api.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=10
stdout_capture_maxbytes=1MB
stderr_logfile=/var/log/cue-api.err
stderr_logfile_maxbytes=1MB
stderr_logfile_backups=10
stderr_capture_maxbytes=1MB
EOF
cat > /etc/supervisor/conf.d/cueworker.conf<< EOF
[program:cue-worker]
command=cue-worker --debug --config-file /etc/cue/worker.conf
process_name=%(program_name)s
stdout_logfile=/var/log/cue-worker.log
stdout_logfile_maxbytes=1MB
stdout_logfile_backups=10
stdout_capture_maxbytes=1MB
stderr_logfile=/var/log/cue-worker.err
stderr_logfile_maxbytes=1MB
stderr_logfile_backups=10
stderr_capture_maxbytes=1MB
EOF
service supervisor restart
