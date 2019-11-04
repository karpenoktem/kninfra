{
  vipassana = { pkgs, config, ... }: {
    # generic config for the server
    imports = [ ./services ];
    nixpkgs.overlays = [ (import ./packages) ];
    environment.systemPackages = with pkgs; [
      htop iftop iotop ncdu
      python3.pkgs.ipython
      # ipython 6 does not support python2
      psmisc socat
      git
      neomutt
    ];
    # environment.noXlibs = true; # smaller, but not cached
    programs.vim.defaultEditor = true;
    environment.etc."vimrc".source = ../salt/states/common/vimrc;
    i18n.supportedLocales = [
      "en_US.UTF-8/UTF-8"
      "nl_NL.UTF-8/UTF-8"
    ];
    users.motd = ''
     ___   _____   __  __ __                    _  __     __   __   
    / _ | / __/ | / / / //_/__ ________  ___   / |/ /__  / /__/ /____ __ _ 
   / __ |_\ \ | |/ / / ,< / _ `/ __/ _ \/ -_) /    / _ \/  '_/ __/ -_)  ' \
  /_/ |_/___/ |___/ /_/|_|\_,_/_/ / .__/\__/ /_/|_/\___/_/\_\\__/\__/_/_/_/
               ${config.networking.hostName}  /_/        dienstenserver
    '';
    services = {
      logcheck = {
        enable = true;
        extraRulesDirs = [
          (builtins.fetchGit https://github.com/bwesterb/x-logcheck)
        ];
      };
      postfix.enable = true;
      openssh.enable = true;
      sshguard = {
        enable = true;
        whitelist = [
          "127.0.0.0/8"
          "10.0.0.0/24"
          "37.251.64.47/32"
          "82.93.241.107/32"
          "82.94.240.40/32"
          "37.252.124.223/32"
          "sw.w-nz.com"
          "62.163.41.99/32"
        ];
      };
    };
    networking.hostName = "vipassana.karpenoktem.nl";
    kn = {
      wiki.enable = false;
      mailman.enable = false;
      django.enable = true;
    };
    networking.firewall.allowedTCPPorts = [ 80 443 ];
  };
  virt = {
    # merged-in config for virtualized system
    users.users.root.openssh.authorizedKeys.keyFiles = [
      ./vm-ssh.key.pub
    ];
    services.mingetty = {
      autologinUser = "root";
      helpLine = ''
        ssh access:
          ./result/bin/ssh
        update running system (does not survive reboot):
          nix-build -A vm && ./result/bin/switch-running-vm
        website:
          http://localhost:8080/
      '';
    };
    virtualisation = {
      # set up serial console
      graphics = false;
      qemu = {
        options = [ "-serial mon:stdio" ];
        # forward port 22 to 2222 and port 80 to 8080
        networkingOptions = [
          "-net nic,netdev=user.0,model=virtio"
          "-netdev user,id=user.0,hostfwd=tcp::2222-:22,hostfwd=tcp::8080-:80\${QEMU_NET_OPTS:+,$QEMU_NET_OPTS}"
        ];
      };
    };
  };
}
