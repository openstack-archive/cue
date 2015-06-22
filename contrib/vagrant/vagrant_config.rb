# -*- mode: ruby -*-
# # vi: set ft=ruby :

# Uncomment $hostname and set it to specify an explicit hostname for the VM
# $hostname = "dev"

# Setup a guest port => host port mapping for the mappings provided below
#$forwarded_port = {
#  8795 => 8795,
#  6080 => 6080,
#  80 => 8080
#}

# Ubuntu box
$ubuntu_box = "sputnik13/trusty64"

# Fedora box
$fedora_box = "box-cutter/fedora20"

# Specify a proxy to be used for packages
# $package_proxy = "http://192.168.41.19:8000/"

# Install devstack in the VM
$install_devstack = true

# Install build dependencies
$install_build_deps = true

# Set $install_tmate to true to
$install_tmate = false

# Set the amount of RAM configured for the VM
$vm_memory = 4096

# Set the number of CPU cores configured for the VM
$vm_cpus = 2
