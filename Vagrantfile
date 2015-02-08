Vagrant.configure(2) do |config|
    # See https://docs.vagrantup.com/v2/multi-machine/
    def common(config, hostname)
        config.vm.box = "chef/debian-7.7"
        config.vm.hostname = "vagrant-" + hostname
        config.vm.box_url = "https://atlas.hashicorp.com/chef/boxes/" \
               + "debian-7.7/versions/1.0.0/providers/virtualbox.box"
        config.vm.synced_folder "salt/states", "/srv/salt"
        config.vm.synced_folder "salt/pillar", "/srv/pillar"
        config.vm.provision :salt do |salt|
            salt.run_highstate = true
            salt.verbose = true
            salt.minion_config = "salt/vagrant_minion_config"
        end
    end

    config.vm.define "sankhara", primary: true do |config|
        common config, "sankhara"
        config.vm.network :public_network
    end

    config.vm.define "phassa" do |config|
        common config, "phassa"
        config.vm.network :public_network
    end
end

# vi: set ft=ruby :
