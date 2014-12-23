# Common provisioning steps for Ubuntu VMs
def ubuntu_common(machine)
  machine.vm.box = $ubuntu_box

  machine.vm.provision :shell, :privileged => true,
    :inline => "DEBIAN_FRONTEND=noninteractive apt-get update"
  machine.vm.provision :shell, :privileged => true,
    :inline => "DEBIAN_FRONTEND=noninteractive apt-get install --yes git"
  machine.vm.provision :shell, :privileged => true,
    :inline => "DEBIAN_FRONTEND=noninteractive apt-get install --yes python-software-properties software-properties-common squid-deb-proxy-client"

  if $package_proxy
    machine.vm.provision :shell, :privileged => true,
      :inline => "echo \"Acquire { Retries \\\"0\\\"; HTTP { Proxy \\\"#{$package_proxy}\\\"; }; };\" > /etc/apt/apt.conf.d/99proxy"
  end

  # Install build dependencies
  if $install_build_deps
    machine.vm.provision "shell", inline: "apt-get install -y build-essential git libmysqlclient-dev python-tox python-dev libxml2-dev libxslt1-dev libffi-dev libssl-dev gettext"
  end

  # Install tmate [optional]
  if $install_tmate
    machine.vm.provision "shell", :inline => "sudo add-apt-repository ppa:nviennot/tmate"
    machine.vm.provision "shell", :inline => "sudo apt-get update"
    machine.vm.provision "shell", :inline => "sudo apt-get install -y tmate"
  end

  # Remove anything unnecessary
  machine.vm.provision "shell", inline: "apt-get autoremove -y"
end
