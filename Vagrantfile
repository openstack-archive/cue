VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.hostname = "cuedev"
  config.vm.network "forwarded_port", guest: 8795, host: 8795

  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
    v.cpus = 2
  end

  config.vm.provider "vmware_fusion" do |v, override|
    v.vmx["memsize"] = "1024"
    v.vmx["numvcpus"] = "2"
    override.vm.box = "puphpet/ubuntu1404-x64"
  end

  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  # Update package list first and ensure package/repository management tools are present
  config.vm.provision "shell", inline: "sudo apt-get update"
  config.vm.provision "shell", inline: "sudo apt-get install -y python-software-properties software-properties-common"

  # Install tmate [optional]
  config.vm.provision "shell", inline: "sudo add-apt-repository ppa:nviennot/tmate"
  config.vm.provision "shell", inline: "sudo apt-get update"
  config.vm.provision "shell", inline: "sudo apt-get install -y tmate"

  # Install dependencies
  config.vm.provision "shell", inline: "apt-get install -y build-essential git libmysqlclient-dev python-tox python-dev libxml2-dev libxslt1-dev libffi-dev libssl-dev gettext"

  # Remove anything unnecessary
  config.vm.provision "shell", inline: "apt-get autoremove -y"

  # Initialize project and environment
  config.vm.provision "shell", inline: "pushd /vagrant && tox ; true"
  config.vm.provision "shell", inline: "source /vagrant/.tox/py27/bin/activate ; pushd /vagrant && python setup.py develop"
  config.vm.provision "shell", inline: "echo 'source /vagrant/.tox/py27/bin/activate' >> ~root/.profile"

end
