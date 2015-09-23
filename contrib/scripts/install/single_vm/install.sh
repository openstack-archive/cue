#!/bin/bash

while test $# -gt 0; do
        case "$1" in
                -h|--help)
                        echo "Single VM Cue Installer"
                        echo " "
                        echo "--h   show brief help"
                        echo "Required parameters:"
                        echo "--image IMAGE_ID   specify Nova image id to use"
                        echo "--flavor FLAVOR_ID  specify a Nova flavor id to use"
                        echo "--cue-management-nic CUE_MANAGEMENT_NIC  specify management network interface for cue"
                        echo "--cue-image CUE_IMAGE_ID  specify a Nova image id for Cue cluster VMs"
                        echo "Optional parameters:"
                        echo "--security-groups SECURITY_GROUPS   specify security group"
                        echo "--key-name KEY_NAME   specify key-name to forward"
                        echo "--nic NIC   a network to attach Cue VM on"
                        echo "--mysql-root-password MYSQL_ROOT_PASSWORD   specify root password for MySql Server"
                        echo "--mysql-cueapi-password MYSQL_CUEAPI_PASSWORD  specify cue api user password for MySql Server"
                        echo "--mysql-cueworker-password MYSQL_CUEWORKER_PASSWORD  specify cue worker user password for MySql Server"
                        exit 0
                        ;;
                --image)
                        shift
                        if test $# -gt 0; then
                                export IMAGE_ID=$1
                        fi
                        shift
                        ;;
                --flavor)
                        shift
                        if test $# -gt 0; then
                                export FLAVOR_ID=$1
                        fi
                        shift
                        ;;
                --cue-management-nic)
                        shift
                        if test $# -gt 0; then
                                export CUE_MANAGEMENT_NIC=$1
                        fi
                        shift
                        ;;
                --cue-image)
                        shift
                        if test $# -gt 0; then
                                export CUE_IMAGE_ID=$1
                        fi
                        shift
                        ;;
                --security-groups)
                        shift
                        if test $# -gt 0; then
                                export SECURITY_GROUPS=$1
                        fi
                        shift
                        ;;
                --cue-security-group)
                        shift
                        if test $# -gt 0; then
                                export CUE_SECURITY_GROUP=$1
                        fi
                        shift
                        ;;
                --key-name)
                        shift
                        if test $# -gt 0; then
                                export KEY_NAME=$1
                        fi
                        shift
                        ;;
                --os-key-name)
                        shift
                        if test $# -gt 0; then
                                export OS_KEY_NAME=$1
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
                --mysql-root-password)
                        shift
                        if test $# -gt 0; then
                                export MYSQL_ROOT_PASSWORD=$1
                        fi
                        shift
                        ;;
                --mysql-cueapi-password)
                        shift
                        if test $# -gt 0; then
                                export MYSQL_CUEAPI_PASSWORD=$1
                        fi
                        shift
                        ;;
                --mysql-cueworker-password)
                        shift
                        if test $# -gt 0; then
                                export MYSQL_CUEWORKER_PASSWORD=$1
                        fi
                        shift
                        ;;
                --floating-ip)
                        shift
                        if test $# -gt 0; then
                                export FLOATING_IP=$1
                        fi
                        shift
                        ;;
                *)
                        break
                        ;;
        esac
done

# verify required and optional input arguments
if [ -z ${IMAGE_ID} ] || [ -z ${FLAVOR_ID} ] || [ -z ${CUE_IMAGE_ID} ] || [ -z ${CUE_MANAGEMENT_NIC} ]; then
    echo "IMAGE_ID, FLAVOR_ID, CUE_IMAGE_ID AND CUE_MANAGEMENT_NIC must be provided"
    exit 1
fi

if [ -z ${MYSQL_ROOT_PASSWORD} ]; then
    MYSQL_ROOT_PASSWORD="password"
fi
if [ -z ${MYSQL_CUEAPI_PASSWORD} ]; then
    MYSQL_CUEAPI_PASSWORD="cuepassword"
fi
if [ -z ${MYSQL_CUEWORKER_PASSWORD} ]; then
    MYSQL_CUEWORKER_PASSWORD="workerpassword"
fi

# set parameters required by mo to fill-in template file
export MYSQL_ROOT_PASSWORD
export MYSQL_CUEAPI_PASSWORD
export MYSQL_CUEWORKER_PASSWORD

# set working directory to script location
PROJECT_ROOT=$( cd $(dirname "$0") && pwd)
pushd ${PROJECT_ROOT}

# Configure user data script from template file
USERDATA_FILE=$(mktemp -t cue_install.XXXX)
chmod +x mo
cat user_data_template | ./mo > ${USERDATA_FILE}

# unset exported parameters from above
unset MYSQL_ROOT_PASSWORD
unset MYSQL_CUEAPI_PASSWORD
unset MYSQL_CUEWORKER_PASSWORD

# Compose Nova boot command string
NOVA_BOOT_BASE="nova boot"
VM_NAME="cue_host"

NOVA_BOOT_COMMAND="${NOVA_BOOT_BASE} --flavor ${FLAVOR_ID} --image ${IMAGE_ID}"
if [ ! -z ${SECURITY_GROUPS} ]; then
    NOVA_BOOT_COMMAND="${NOVA_BOOT_COMMAND} --security-groups ${SECURITY_GROUPS}"
fi

if [ ! -z ${KEY_NAME} ]; then
    NOVA_BOOT_COMMAND="${NOVA_BOOT_COMMAND} --key-name ${KEY_NAME}"
fi

OS_KEYNAME=${OS_KEYNAME:-$KEY_NAME}

if [ ! -z ${NIC} ]; then
    NOVA_BOOT_COMMAND="${NOVA_BOOT_COMMAND} --nic net-id=${NIC}"
fi

if [ ! -z ${CUE_MANAGEMENT_NIC} ]; then
    NOVA_BOOT_COMMAND="${NOVA_BOOT_COMMAND} --nic net-id=${CUE_MANAGEMENT_NIC}"
fi

NOVA_BOOT_COMMAND="${NOVA_BOOT_COMMAND} --user-data ${USERDATA_FILE} ${VM_NAME}"
eval ${NOVA_BOOT_COMMAND}

if [ ! -z ${FLOATING_IP}  ]; then
    echo "Waiting for cue_host VM to go ACTIVE..."
    while [ -z "$(nova show $VM_NAME 2>/dev/null | egrep 'ACTIVE|ERROR')" ]; do
        sleep 1
    done
    nova floating-ip-associate $VM_NAME ${FLOATING_IP}
fi

rm ${USERDATA_FILE}
popd
