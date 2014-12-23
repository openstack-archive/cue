# Common provisioning steps for Fedora VMs
def fedora_common(machine)
  machine.vm.box = $fedora_box

  machine.vm.provision :shell, :privileged => true, :inline => "yum update -y vim-minimal" # RH Bug 1066983
  machine.vm.provision :shell, :privileged => true, :inline => "yum install -y git-core MySQL-python"
end
