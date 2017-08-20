# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|

  config.vm.box = "ubuntu/trusty64"

  config.vm.network "forwarded_port", guest: 5000, host: 5000

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
  end

  config.vm.provision "shell", privileged: false,  inline: <<-SHELL
    sudo apt-get update
    sudo apt-get install -y build-essential python-pip
    sudo pip install --upgrade pip
    cd /vagrant
    sudo pip install -r requirements.txt
  SHELL
end