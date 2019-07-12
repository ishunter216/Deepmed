PROJECT_NAME = "deepmed"
BACKEND_DIR = "/home/ubuntu/#{PROJECT_NAME}/src/backend"
FRONTEND_DIR = "/home/ubuntu/#{PROJECT_NAME}/src/frontend"

Vagrant.require_version ">= 1.8.1"
Vagrant.configure(2) do |config|

  config.vm.hostname = PROJECT_NAME
  config.vm.box = "ubuntu/xenial64"

  config.vm.network :private_network, ip: "192.168.44.77"
  config.vm.synced_folder "./backend", BACKEND_DIR
  config.vm.synced_folder "./frontend", FRONTEND_DIR

  config.vm.provider :virtualbox do |vb|
    vb.name = PROJECT_NAME
    vb.memory = "1024"
    vb.cpus = 1
    vb.gui = false
  end

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "ansible/site.yml"
    ansible.inventory_path = "ansible/vagrant.ini"
    ansible.host_key_checking = false
    ansible.limit = "*"
  end
end