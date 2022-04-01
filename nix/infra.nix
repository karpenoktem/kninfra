let
  # TODO: ldap security
  globals.passwords.ldap = {
    infra = "asdf";
    daan = "asdf";
    saslauthd = "asdf";
  };

in
{
  # config for the server (both real and VM)
  vipassana = { pkgs, lib, config, ... }: {
    # import ./services/default.nix, which imports the other files there
    # this way, we have access to the kn.django module
    imports = [ ./services ];
    # define a package overlay, see ./packages/default.nix
    nixpkgs.overlays = [ (import ./packages) ];
    environment.systemPackages = with pkgs; [
      htop iftop iotop ncdu psmisc socat git neomutt
    ];

    # pin things like state file layouts for postgresql
    system.stateVersion = "21.05";

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
        enable = false;
        extraRulesDirs = [
          (builtins.fetchGit {
            url = https://github.com/bwesterb/x-logcheck;
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
        suffix = "dc=karpenoktem,dc=nl";
        domain = "karpenoktem.nl";
      };
      giedo = {
        enable = true;
        ldap.user = "cn=infra,dc=karpenoktem,dc=nl";
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
  # merged-in config for virtualized system
  virt = {
    # install the vm-ssh.key.pub for ssh access
    users.users.root.openssh.authorizedKeys.keyFiles = [
      ./vm-ssh.key.pub
    ];
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
