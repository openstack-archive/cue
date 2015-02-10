# -*- mode: ruby -*-
# # vi: set ft=ruby :

require 'fileutils'

Vagrant.require_version ">= 1.6.0"

CONFIG = File.join(File.dirname(__FILE__), "vagrant_config.rb")

VAGRANTFILE_API_VERSION = "2"

# Devstack init script
$devstack_init = <<SCRIPT
#!/bin/bash
DEBIAN_FRONTEND=noninteractive sudo apt-get -qqy update || sudo yum update -qy
DEBIAN_FRONTEND=noninteractive sudo apt-get install -qqy git || sudo yum install -qy git
pushd ~
git clone https://git.openstack.org/openstack-dev/devstack
pushd devstack
echo '[[local|localrc]]' > local.conf
echo ADMIN_PASSWORD=password >> local.conf
echo MYSQL_PASSWORD=password >> local.conf
echo RABBIT_PASSWORD=password >> local.conf
echo SERVICE_PASSWORD=password >> local.conf
echo SERVICE_TOKEN=tokentoken >> local.conf
echo HOST_IP=127.0.0.1 >> local.conf
echo enable_service n-novnc >> local.conf
echo disable_service n-net >> local.conf
echo enable_service q-svc >> local.conf
echo enable_service q-agt >> local.conf
echo enable_service q-dhcp >> local.conf
echo enable_service q-l3 >> local.conf
echo enable_service q-meta >> local.conf
echo enable_service tempest >> local.conf
./stack.sh
SCRIPT

# Defaults for config options
$hostname = File.basename(File.dirname(__FILE__))
$forwarded_port = 8795
$install_devstack = false
$install_build_deps = true
$install_tmate = false
$vm_memory = 2048
$vm_cpus = 2

if File.exist?(CONFIG)
  require CONFIG
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "cuedev"
  config.vm.network "forwarded_port", guest: $forwarded_port, host: $forwarded_port

  config.vm.provider "virtualbox" do |v|
    v.memory = $vm_memory
    v.cpus = $vm_cpus
  end

  config.vm.provider "vmware_fusion" do |v, override|
    override.vm.box = "sputnik13/trusty64"
    v.vmx["memsize"] = $vm_memory
    v.vmx["numvcpus"] = $vm_cpus
    v.vmx["vhv.enable"] = TRUE
    v.vmx["ethernet0.virtualdev"] = "vmxnet3"
  end

  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  # Update package list first and ensure package/repository management tools are present
  config.vm.provision "shell", inline: "sudo apt-get update"
  config.vm.provision "shell", inline: "sudo apt-get install -y python-software-properties software-properties-common"

  # Install tmate [optional]
  if $install_tmate
    config.vm.provision "shell", inline: "sudo add-apt-repository ppa:nviennot/tmate"
    config.vm.provision "shell", inline: "sudo apt-get update"
    config.vm.provision "shell", inline: "sudo apt-get install -y tmate"
  end

  # Install dependencies
  if $install_build_deps
    config.vm.provision "shell", inline: "apt-get install -y build-essential git libmysqlclient-dev python-tox python-dev libxml2-dev libxslt1-dev libffi-dev libssl-dev gettext"
  end

  # Remove anything unnecessary
  config.vm.provision "shell", inline: "apt-get autoremove -y"

  # Install devstack
  if $install_devstack
    config.vm.provision "shell", inline: $devstack_init, privileged: false
  end

  # Initialize project and environment
  config.vm.provision "shell", inline: "pushd /vagrant && tox ; true"

end
