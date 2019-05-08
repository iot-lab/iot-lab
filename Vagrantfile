Vagrant.configure("2") do |config|
  config.vm.box = "iotlab/iotlab-vm"
  config.ssh.username = "user"
  config.vm.synced_folder ".", "/home/user/iot-lab"
  config.vm.provider "virtualbox" do |v|
    v.name = "iotlab-vm"
  end
end
