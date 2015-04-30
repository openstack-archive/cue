#!/bin/bash

# default cluster values
CLUSTER_NAME=${CLUSTER_NAME:-test_cluster}
CLUSTER_SIZE=${CLUSTER_SIZE:-2}
FLAVOR=${FLAVOR:-8795}

# read input argument for cluster create
while test $# -gt 0; do
        case "$1" in
                -h|--help)
                        echo "Create Cue Cluster"
                        echo " "
                        echo "Required parameters:"                        
                        echo "--name CLUSTER_NAME   specify cluster name"
                        echo "--nic NIC   specify a network_id to attach cluster on"
                        echo "--flavor FLAVOR  specify cluster flavor to use"
                        echo "--size CLUSTER_SIZE  specify size of the cluster"
                        exit 0
                        ;;
                --name)
                        shift
                        if test $# -gt 0; then
                                export CLUSTER_NAME=$1
                        fi
                        shift
                        ;;
                --flavor)
                        shift
                        if test $# -gt 0; then
                                export FLAVOR=$1
                        fi
                        shift
                        ;;
                --size)
                        shift
                        if test $# -gt 0; then
                                export CLUSTER_SIZE=$1
                        fi
                        shift
                        ;;               
                --nic)
                        shift
                        if test $# -gt 0; then
                                export NIC=$1
                        fi
                        shift
                        ;;
                *)
                        break
                        ;;
        esac
done

# exit if network_id is not provided
if [ -z $NIC ]; then 
	echo "please provide a 'NIC'(network_id)"
	exit
fi

# install python-cueclient (assuming git is available)
pip freeze | grep python-cueclient || pip install -e git://git.openstack.org/stackforge/python-cueclient.git#egg=python-cueclient


# create a cluster (assuming env variables for keystone authentication are sourced)
openstack cue cluster create --name $CLUSTER_NAME --nic $NIC --size $CLUSTER_SIZE --flavor $FLAVOR