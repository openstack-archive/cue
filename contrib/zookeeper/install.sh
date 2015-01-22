#!/bin/bash
#
# Script for installing ZooKeeper in both stand alone and  clustered
# configurations.  The script takes as input the ID of the current
# node being provisioned and the IP(s) for all nodes in the ZooKeeper
# cluster (referred in ZooKeeper as a ZooKeeper ensemble).

# Provision 1 node by default
ZOOKEEPER_COUNT=1

# Determine what Linux distribution is being used
if [[ -f '/etc/issue' ]]; then
    LINUX_DISTRO=`cat /etc/issue | egrep 'Amazon|Ubuntu|CentOS|RedHat|Debian' | awk -F' ' '{print $1}'`
fi

# Print usage information
function usage {
    cat << EOF
usage: $0 [-n count] [-h] MYID IP_1 ... IP_N

-n              The number of ZooKeeper nodes in the ensemble
-h              Print this help message

MYID            The current node's ID.  This ID must be unique
                within the ZooKeeper ensemble

IP_1 ... IP_N   List of IP addresses for each node in the
                ZooKeeper ensemble

EOF
    exit -1
}

# Parse option arguments
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

# Verify there are at least as many positional arguments as the
# number of ZK nodes specified in the -n option
if [[ ! $# -gt $ZOOKEEPER_COUNT ]]; then
    echo "Invalid number of arguments"
    echo ""
    usage
fi

# Get this node's ZooKeeper ID
ZK_MYID=$1
shift

# Read the list of ZooKeeper node IPs
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
    'Ubuntu')
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
