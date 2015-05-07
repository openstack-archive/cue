#!/usr/bin/env bash

##
#   This script will take all nodes found in 'nova list' and
#       1) Either take a free Floating IP or create a new one and associate
#           it with the node
#       2) Add the FIP endpoint to the cue database's endpoints table
#
#   Set verbose to 1 to print all the fun stuff.
##

function myecho {

    if [[ $verbose == 1 ]]; then
        echo -e "$1"
    fi
}

function get_floating_ip {
    # First check if we have existing floating ip we can use.
    list_float_out="$(nova floating-ip-list)"
    myecho "nova floating-ip-list:"
    myecho "$list_float_out\n"

    trimmed_list_float_out=$(echo "$list_float_out" | grep '^| [0-9a-f]')

    # Loop over every existing FIP & check if it has an associated static ip
    while read -r line; do
        associated_fixed_ip=$(echo "$line" | cut -f5 -d'|' | tr -d ' ')
        echo "associated_fixed_ip: $associated_fixed_ip"

        if [[ $associated_fixed_ip == "-" ]]; then
            floating_ip=$(echo "$line" | cut -f3 -d'|' | tr -d ' ')
            break
        fi
    done <<< "$trimmed_list_float_out"

    # Check if FIP found
    if [[ ! -z "$floating_ip" ]]; then
        myecho "Using existing floating ip:  $floating_ip \n"
        return
    fi

    myecho "Didn't find a FIP, creating one..."

    # Creates new FIP and parses the IP
    float_create="$(nova floating-ip-create)"
    myecho "nova floating-ip-create:"
    myecho "$float_create\n"

    trimmed_float_create=$(echo "$float_create" | grep '^| [0-9a-f]')
    floating_ip=$(echo "$trimmed_float_create" | cut -f3 -d'|' | tr -d ' ')
    myecho "New floating IP created: $floating_ip"
    return $floating_ip

}

# arg 1 is the floating ip to associate to
# arg 2 is an array of VM IDs
function associate_ip {

    vm_ids=$2

    for vm in ${vm_ids[@]}; do

        associate_out="$(nova floating-ip-associate "$vm" "$1")"
        myecho "Associating  $vm  with Floating IP:  $1"
        myecho "output:\n$associate_out"
    done

}

# arg 1 is the floating ip to disassociate from
# arg 2 is the array of VM IDs
function clear_association {

    vm_ids=$2

    for vm in ${vm_ids[@]}; do

        disassociate_out="$(nova floating-ip-disassociate "$vm" "$1")"
        myecho "Disassociating $vm with Floating IP: $1"
        myecho "-Disassociation out:"
        myecho "$disassociate_out\n"
    done
}

# arg 1 is the floating ip to write in cue db
# arg 2 is the array of VM IDs to write fip to
function write_ip_to_db {

    vm_ids=$2

    # First, print out initial DB state
    read_query="SELECT * FROM endpoints;"
    read_query_out=$(echo "$read_query" | mysql -u root cue)
    myecho "-Endpoints db (before state):\n$read_query_out"
    myecho "-------------------\n"

    for vm in ${vm_ids[@]}; do

        # First need to get the cue node ID using the nova list ID as the cue instance_id
        translate_query="SELECT id FROM nodes WHERE instance_id='$vm';"
        translate_query_out=$(echo "$translate_query" | mysql -u root cue | sed -n 2p)
        myecho "Translate Nova ID to Cue Node ID query: \n$translate_query"
        myecho "Translate query out:\n$translate_query_out"
        myecho "---------------\n"

        write_query="UPDATE endpoints SET uri='$1:5672' WHERE node_id='$translate_query_out';"
        write_query_out=$(echo "$write_query" | mysql -u root cue)
        myecho "Update sql: \n$write_query\n"
        myecho "Write sql out:\n$write_query_out"
        myecho "-------------\n"

    done

    read_query_out=$(echo "$read_query" | mysql -u root cue)
    myecho "-Read sql (after state):\n$read_query_out"
    myecho "-------------------\n"

}

function get_vm_info {
    # Parses nova list output to get the private ip addresses for all nodes
    static_ip_arr=($(nova list | cut -f 7 -d '|' | awk '{for(i=1;i<NF;i++){ if(match($i,"private=")){print $i} } }' | cut -c 9- | cut -f 1 -d ','))

    # Parses nova list output to get IDs for each node
    vm_ids=($(nova list | cut -s -f 2 -d '|'))
    vm_ids=("${vm_ids[@]:1}")


    myecho "-VM IP Addresses:"
    for i in ${static_ip_arr[@]}; do
        myecho $i
    done
    myecho "-----------------\n"

    myecho "-VM IDs:"
    for i in ${vm_ids[@]}; do
        myecho $i
    done
    myecho "-----\n"
}

##
# Start of execution
##
verbose=0

get_floating_ip

if [[ -z "$floating_ip" ]]; then
     myecho "Couldn't find floating ip!  exiting..."
     exit
fi

# Get the IP addresses and IDs of the current cue vms
get_vm_info

if [[ -z "$static_ip_arr" ]]; then
    myecho "Couldn't find the static IPs!  exiting..."
    exit
fi
if [[ -z "vm_ids" ]]; then
    myecho "Couldn't find the VM IDs!  exiting..."
     exit
fi

myecho "Nova list - Before association:"
myecho "$(nova list)\n"

# Associate the new floating IP with each of the cue VMs
associate_ip "$floating_ip" "$vm_ids"

myecho "Nova list - After association:"
myecho "$(nova list)\n"

# Write the floating_ip/endpoint to db
write_ip_to_db "$floating_ip" "$vm_ids"

## Clearing associate for testing
#clear_association "$floating_ip" "$vm_ids"