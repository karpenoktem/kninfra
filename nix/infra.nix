let
  # TODO: ldap security
  globals.passwords.ldap = {
    infra = "asdf";
    daan = "asdf";
    saslauthd = "asdf";
  };
  toLdap = lib: domain:
    with lib;
    concatMapStringsSep "," (x: "dc=${x}") (splitString "." domain);
in rec {
  # config for the server (both real and VM)
  vipassana = { pkgs, lib, config, ... }: {
    # import ./services/default.nix, which imports the other files there
    # this way, we have access to the kn.django module
    imports = [ ./services ];
    # define a package overlay, see ./packages/default.nix
    nixpkgs.overlays = [ (import ./packages) ];
    environment.systemPackages = with pkgs; [
      htop
      iftop
      iotop
      ncdu
      psmisc
      socat
      git
      neomutt
    ];

    # pin things like state file layouts for postgresql
    system.stateVersion = "21.05";

    users.mutableUsers = false;
    time.timeZone = "Europe/Amsterdam";
    # this changes some packages so that there is no X dependency
    # allowing for the total system size to be smaller.
    # however, these builds are not cached by cache.nixos.org, so
    # the build will take longer:
    # environment.noXlibs = true;

    # set EDITOR to vim
    programs.vim.defaultEditor = true;
    # this installs /etc/vimrc
    environment.etc."vimrc".source = ../salt/states/common/vimrc;
    # install en_US and nl_NL locales
    i18n.supportedLocales = [ "en_US.UTF-8/UTF-8" "nl_NL.UTF-8/UTF-8" ];
    users.motd = ''
         ___   _____   __  __ __                    _  __     __   __   
        / _ | / __/ | / / / //_/__ ________  ___   / |/ /__  / /__/ /____ __ _ 
       / __ |_\ \ | |/ / / ,< / _ `/ __/ _ \/ -_) /    / _ \/  '_/ __/ -_)  ' \
      /_/ |_/___/ |___/ /_/|_|\_,_/_/ / .__/\__/ /_/|_/\___/_/\_\\__/\__/_/_/_/
                   ${config.networking.hostName}  /_/        dienstenserver
        '';
    services = {
      logcheck = {
        enable = false;
        extraRulesDirs = [
          (builtins.fetchGit {
            url = "https://github.com/bwesterb/x-logcheck";
            rev = "3180507e96b317984e22e9ca01771f106190b0ef";
          })
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
    networking.hostName = "vipassana";
    networking.domain = "karpenoktem.nl";
    # enable/disable various KN services
    kn = {
      shared.enable = true;
      shared.initialDB = true;
      wiki.enable = true;
      #mailman.enable = true; # TODO
      django.enable = true;
      daan.enable = true;
      daan.ldap.pass = globals.passwords.ldap.daan;
      hans.enable = true;
      ldap = {
        enable = true;
        suffix = toLdap lib config.networking.domain;
        domain = config.networking.domain;
      };
      giedo = {
        enable = true;
        ldap.user = "cn=infra,${config.lda.suffix}";
        ldap.pass = globals.passwords.ldap.giedo;
      };
    };
    # allow remote http, ssh access
    networking.firewall.allowedTCPPorts = lib.mkForce [ 22 80 443 ];
    services.mailman2.enable = true;
    services.saslauthd = {
      enable = true;
      # todo: start after slapd?
      package = pkgs.cyrus_sasl.override { enableLdap = true; };
      mechanism = "ldap";
      # todo: ldapi peer auth, eliminates saslauthd password
      config = ''
        ldap_servers: ldap://localhost
        ldap_search_base: ou=users,${config.kn.ldap.suffix}
        ldap_filter: (uid=%u)
        ldap_bind_dn: cn=saslauthd,${config.kn.ldap.suffix}
        ldap_bind_pw: ${globals.passwords.ldap.saslauthd}
      '';
    };
  };
  staging = { lib, ... }: {
    # nixos-rebuild switch --flake '.#staging' --target-host root@dev.kn.cx --build-host localhost
    imports = [ vipassana hetzner ];
    networking = {
      hostName = lib.mkForce "staging";
      domain = lib.mkForce "dev.kn.cx";
      interfaces.eth0.ipv6.addresses = [{
        address = "2a01:4f8:c17:4eec::";
        prefixLength = 64;
      }];
    };
    users.users.root = {
      openssh.authorizedKeys.keys = [
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDo1N5E6qkb3McJOvv0PqI7E8iYLAcjil5RWc+zeTtN/ yorick"
        "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCbieYUtRGQ4nf4glQvrZDn72doP6W2uw2z9VqFq5sZLROXYa4jW8nwx4h+BiArGs+VPwn6lfsP19PX6yNIk74C/SkO26S1Zvbe7ffNusi6PH2BQIOWeAYKk+eZH+ZOeD8z07uDB7QffwRLwzSaPFg+zfRzsMFoXH/GE9qOQ4lnfk8czTZL7zbZf/yS7mDFztClXFciYsVwgRXNiFpfc+9mOkU0oBWtGo/WGUhB0Hds3a4ylyjjVAcC/l1H2bvc/Q3d6bbn23pUFl2V78Yg1B4b1MT34qbBV6whXAQd7KM9tND2ZhpF2XQ7Spi1QlOac0jup+sE+3bbvcjNqTI05DwJO/dX5F2gSAFkvSY4ZPqSX5ilE/hj4DQuhRgLmQdbVl5IFV9aLYqUvJcCqX9jRFMly4YTFXsFz18rGkxOYGZabcE1usBM2zRVDTtEP6Si5ii76Ocvp8aNFBB2Kf1whg8tziTv3kQEQ9fd2sRtE2J3xveJiwXjUBU2uikSOKe8JP47Tb6PYlv7Ty/6OI51aUQn++R72VNajdBJ1r1osp7leqTJ+sXuLlWLo/a7lDpDmgEI7dbxqmpjLcMce0JzqLKlP1Q2U/nkYy86xkjSTH1rNUI2JAbJx3iTcGy7bq12yfjNfcGAqY4GVXvisK1cpbF0RCjaFExwtmzorljHh6ZHjQ== lars"
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINbmv5LOl+qu5tKTaaUq49Jciv3S3hrI4hwVWBh7Spl6 ayke"
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBWqwvAk43sLon1UtP/Swl2hRhetG1OmLCrfGp4tBr6V ayke@karpenoktem"
      ];
      # pass yorick/kn/stage
      hashedPassword =
        "$6$2ngK32gHW3AsOFOS$G/nsXxPUi9ePaa0gOrNaNN1nBDSYfeDkLdWZI3ad05jdvdyzMoCzZC/YFn8lFO1CLapKSQFStLgI3HPqPy1/h0";
    };
    kn.shared.initialDB = true;
    # for now, be absolutely sure about exposed services
    # until I've fixed the passwords :D
    networking.firewall.allowedUDPPorts = lib.mkForce [ ];
    networking.firewall.allowedTCPPorts = lib.mkOverride 49 [ 22 ]; # 80 443
    nix.binaryCaches = [
      "https://cache.nixos.org"
      "https://kninfra.cachix.org"
    ];
    nix.binaryCachePublicKeys = [
      "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
      "kninfra.cachix.org-1:l6SeUehzysoUHUX86/gmqiWaa9Jy7dTSFnPcWGw3zGo="
    ];
  };
  hetzner = { modulesPath, ... }: {
    # installation:
    # make hetzner cloud, mount nixos 21.11 iso
    # rescue console, curl https://pub.yori.cc/install-hetzner.sh | bash
    # unmount, restart server, login with yorick's ssh key
    imports = [ (modulesPath + "/profiles/qemu-guest.nix") ];
    boot.loader.grub = {
      enable = true;
      version = 2;
      devices = [ "/dev/sda" ];
    };
    networking.usePredictableInterfaceNames = false;
    networking.useDHCP = false;
    networking.interfaces.eth0 = { useDHCP = true; };
    networking.defaultGateway6 = {
      address = "fe80::1";
      interface = "eth0";
    };
    services.openssh.permitRootLogin = "prohibit-password";

    boot.initrd.availableKernelModules =
      [ "ahci" "xhci_pci" "virtio_pci" "sd_mod" "sr_mod" ];
    boot.initrd.kernelModules = [ ];
    boot.kernelModules = [ ];
    boot.extraModulePackages = [ ];

    fileSystems."/" = {
      device = "/dev/sda1";
      fsType = "ext4";
    };

    swapDevices = [ ];

    hardware.cpu.amd.updateMicrocode = true;
  };
  # merged-in config for virtualized system
  virt = {
    # install the vm-ssh.key.pub for ssh access
    users.users.root.openssh.authorizedKeys.keyFiles = [ ./vm-ssh.key.pub ];
    kn.shared.initialDB = true;
    services.getty = {
      autologinUser = "root";
      helpLine = ''
        ssh access:
          ./result/bin/ssh
        update running system (does not survive reboot):
          nix-build -A vm && ./result/bin/switch-running-vm
        website:
          http://localhost:8080/
        to get out:
          poweroff
      '';
    };
    # qemu settings:
    virtualisation = {
      memorySize = 1024;
      diskSize = 1024;
      # set up serial console
      graphics = false;
      qemu = {
        options = [ "-serial mon:stdio" ];
        # forward port 22 to 2222 and port 80 to 8080
        # based on the default in nixpkgs
        networkingOptions = [
          "-net nic,netdev=user.0,model=virtio"
          "-netdev user,id=user.0,hostfwd=tcp::2222-:22,hostfwd=tcp::8080-:80\${QEMU_NET_OPTS:+,$QEMU_NET_OPTS}"
        ];
      };
    };
  };
}
