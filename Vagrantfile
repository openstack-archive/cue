VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
    v.cpus = 2
  end
  config.vm.box = "ubuntu/trusty64"
  config.vm.network "forwarded_port", guest: 8795, host: 8795

  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
  # Install tmate
  config.vm.provision "shell", inline: "sudo apt-get install python-software-properties && sudo add-apt-repository ppa:nviennot/tmate && sudo apt-get update && sudo apt-get install tmate"

  # Install dependencies and remove anything unnecessary
  config.vm.provision "shell", inline: "apt-get install -y build-essential git libmysqlclient-dev python-tox python-dev libxml2-dev libxslt1-dev libffi-dev libssl-dev gettext"
  config.vm.provision "shell", inline: "apt-get autoremove -y"

  # Initialize project and environment
  config.vm.provision "shell", inline: "pushd /vagrant && tox"
  config.vm.provision "shell", inline: "echo 'source /vagrant/.tox/py27/bin/activate' >> ~vagrant/.profile"
  config.vm.provision "shell", inline: "sudo -u vagrant python setup.py develop"
end
