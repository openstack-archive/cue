#!/bin/bash

ZOOKEEPER_COUNT=1

if [[ -f '/etc/issue' ]]; then
    LINUX_DISTRO=`cat /etc/issue | egrep 'Amazon|Ubuntu|CentOS|RedHat|Debian' | awk -F' ' '{print $1}'`
fi

function usage {
    echo "usage: $0 [-n count] [-h] MYID IP_1 ... IP_N"
    exit -1
}

while getopts n:h opt; do
    case $opt in
        n)
            ZOOKEEPER_COUNT=$OPTARG
            ;;
        h)
            usage
    esac
done

# Pop processed options from the option stack
OPTIND=$OPTIND-1
shift $OPTIND

if [[ ! $# -gt $ZOOKEEPER_COUNT ]]; then
    echo "Invalid number of arguments"
    echo ""
    usage
fi

ZK_MYID=$1
shift

for i in `seq 1 $ZOOKEEPER_COUNT`; do
    ZK_SERVER_IP[$i]=$1
    shift
done

# Check for root permissions
if [ "$(id -u)" != "0" ]; then
    SUDO='sudo'
    echo ""
    echo "This script is not being run as root, you may be asked for a password in order to execute sudo.."
    echo ""
else
    SUDO=
fi

# Set distro specific values
case "$LINUX_DISTRO" in
    'Ubuntu'|'Debian')
        UPDATE_PKG='apt-get update'
        INSTALL_PKG='apt-get install -y'
        PKG_NAME='zookeeper zookeeper-bin zookeeperd'
        CONFIG_FILE='/etc/zookeeper/conf/zoo.cfg'
        SERVICE_NAME='zookeeper'
        MYID_FILE='/var/lib/zookeeper/myid'
        ;;

    *)
        echo "Only Ubuntu is supported at this time"
        exit -1
esac

# Update package cache if necessary
if $UPDATE_PKG; then
    $SUDO $UPDATE_PKG
fi

# Install package
$SUDO $INSTALL_PKG $PKG_NAME

# Generate configuration
$SUDO sed -i.bak -e '/^#.*$/d' -e '/^$/d' -e '/^server\..*=.*/d' $CONFIG_FILE
for i in `seq 1 $ZOOKEEPER_COUNT`; do
    echo "server.${i}=${ZK_SERVER_IP[$i]}:2888:3888" >> $CONFIG_FILE
done

echo $ZK_MYID > $MYID_FILE

# Restart service
$SUDO service $SERVICE_NAME restart
