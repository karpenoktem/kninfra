let
  # user keys are specified in ./users.toml
  users = builtins.fromTOML (builtins.readFile ./users.toml);
  userList = builtins.attrValues users;
  sshKeys = production:
    builtins.concatMap (x: x.sshkeys)
    (builtins.filter (x: production -> x.production) userList);
in rec {
  # shared config for the server (both real and VM)
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

    # manage users from the nixos configuration
    users.mutableUsers = false;

    time.timeZone = "Europe/Amsterdam";
    # this changes some packages so that there is no X dependency
    # allowing for the total system size to be smaller.
    # however, these builds are not cached by cache.nixos.org, so
    # the build will take longer:
    # environment.noXlibs = true;

    # set up agenix secret
    age.secrets.kn-env = { };

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
      openssh = {
        enable = true;
        passwordAuthentication = false;
        permitRootLogin = "prohibit-password";
      };
      sshguard = {
        enable = true;
        whitelist = [
          "127.0.0.0/8"
          "10.0.0.0/24"
          "37.251.64.47/32"
          "82.93.241.107/32"
          "82.94.240.40/32"
          "37.252.124.223/32"
          #"sw.w-nz.com"
          "62.163.41.99/32"
        ] ++ (lib.concatMap (x: x.allowed-ips) userList);
      };
    };
    networking = {
      hostName = "vipassana";
      domain = "karpenoktem.nl";
    };
    security.acme = {
      acceptTerms = true;
      # slightly obfuscated against spammers
      defaults.email = lib.concatStringsSep "@" [ "webcie" "karpenoktem.nl" ];
    };
    # enable/disable various KN services
    kn = {
      shared.enable = true;
      shared.initialDB = true;
      wiki.enable = true;
      #mailman.enable = true; # TODO
      django.enable = true;
      daan.enable = true;
      hans.enable = true;
      rimapd.enable = true;
      giedo.enable = true;
    };
    # allow remote http, ssh access
    networking.firewall = {
      allowedTCPPorts = lib.mkForce [ 22 80 443 ];
      allowedUDPPorts = lib.mkForce [ ];
    };
    services.mailman2.enable = true;
    services.saslauthd = {
      enable = true;
      mechanism = "rimap";
    };
    # TODO(upstream) to nixpkgs
    # upstream currently doesn't support the config scheme for this mechanism
    systemd.services.saslauthd.serviceConfig.ExecStart =
      let cfg = config.services.saslauthd;
      in lib.mkForce
      "@${cfg.package}/sbin/saslauthd saslauthd -a ${cfg.mechanism} -O 127.0.0.1/${
        toString config.kn.rimapd.port
      }";
    nix.binaryCaches =
      [ "https://cache.nixos.org" "https://kninfra.cachix.org" ];
    nix.binaryCachePublicKeys = [
      "cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY="
      "kninfra.cachix.org-1:l6SeUehzysoUHUX86/gmqiWaa9Jy7dTSFnPcWGw3zGo="
    ];
  };

  staging = { lib, ... }: {
    # nixos-rebuild switch --flake '.#staging' --target-host root@dev.kn.cx --build-host localhost
    imports = [ vipassana ./hetzner.nix ];
    networking = {
      hostName = lib.mkForce "staging";
      domain = lib.mkForce "dev.kn.cx";
      interfaces.eth0.ipv6.addresses = [{
        address = "2a01:4f8:c17:4eec::";
        prefixLength = 64;
      }];
    };
    services.nginx.virtualHosts.kn = {
      serverName = "dev.kn.cx";
      enableACME = true;
      forceSSL = true;
    };
    age.secrets.kn-env.file = ../secrets/staging.age;
    users.users.root = {
      # add non-production ssh access
      openssh.authorizedKeys.keys = sshKeys false;
      # pass yorick/kn/stage
      hashedPassword =
        "$6$2ngK32gHW3AsOFOS$G/nsXxPUi9ePaa0gOrNaNN1nBDSYfeDkLdWZI3ad05jdvdyzMoCzZC/YFn8lFO1CLapKSQFStLgI3HPqPy1/h0";
    };
    kn.shared.initialDB = true;
    # don't log these, there are *a lot*
    networking.firewall.logRefusedConnections = false;
  };

  # mixin for virtual system (development vm, vm-tests)
  virtualized = {
    imports = [ vipassana ];
    # set up vm hostkey
    # obfuscated using b64 to avoid false positives in security scanners
    system.activationScripts.hostkey.text = ''
      mkdir -p /root
      base64 -d ${./vm-host.key.b64} > /root/vm-host.key
      chmod 0600 /root/vm-host.key
    '';
    system.activationScripts.agenixRoot.deps = [ "hostkey" ];
    services.openssh.hostKeys = [{
      path = "/root/vm-host.key";
      type = "ed25519";
    }];
    services.nginx.virtualHosts.kn.serverName = "localhost";
    age.secrets.kn-env.file = ../secrets/vm.age;
    kn.shared.initialDB = true;
  };

  # virtualized system, used for development
  vm = { modulesPath, pkgs, ... }: {
    imports = [ virtualized "${modulesPath}/virtualisation/qemu-vm.nix" ];
    # install the vm-ssh.key.pub for ssh access
    users.users.root.openssh.authorizedKeys.keyFiles = [ ./vm-ssh.key.pub ];
    services.getty = {
      autologinUser = "root";
      helpLine = ''
        ssh access:
          vm.ssh
        update running system (does not survive reboot):
          vm.deploy
        website:
          http://localhost:8080/
        to get out:
          vm.stop
      '';
    };
    kn.django.package = "/kninfra-pub";
    programs.bash.shellAliases."vm.stop" = "poweroff";
    system.fsPackages = [ pkgs.bindfs ];
    # qemu settings:
    virtualisation = {
      memorySize = 1024;
      diskSize = 1024;
      # set up serial console
      graphics = false;
      # Share the PRJ_ROOT into the vm
      sharedDirectories.kninfra = {
        source = "\${PRJ_ROOT:?please run this inside the devshell}";
        target = "/kninfra";
      };
      # use bindfs to make it world-readable
      fileSystems."/kninfra-pub" = {
        depends = [ "/kninfra" ];
        device = "/kninfra";
        fsType = "fuse.bindfs";
        options = [ "ro" "perms=0555" ];
      };
      forwardPorts = [
        {
          host.port = 8080;
          guest.port = 80;
        }
        {
          host.port = 2222;
          guest.port = 22;
        }
      ];
      qemu = { options = [ "-serial mon:stdio" ]; };
    };
  };
}
