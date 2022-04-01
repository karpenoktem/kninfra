{pkgs, lib, config, ...}:
let
  cfg = config.kn.daan;
in
{
  options.kn.daan = with lib; {
    enable = mkEnableOption "KN Daan";
    socket = mkOption {
      default = "/run/infra/daan";
      description = "The socket path to use for Daan";
      type = types.path;
    };
    ldap.user = mkOption {
      type = types.str;
      default = "cn=daan,dc=karpenoktem,dc=nl"; # todo suffix
    };
    ldap.pass = mkOption {
      type = types.str;
    };
    
  };
  config = lib.mkIf cfg.enable {
    systemd.sockets.daan = {
      wantedBy = [ "sockets.target" ];
      listenStreams = [ cfg.socket ];
      socketConfig = {
        SocketGroup = "infra";
        SocketMode = "0660";
      };
    };
    systemd.services.daan = rec {
      requires = [ "initialize_ldap.service" "postfix.service" ];
      after = requires ++ [ "mediawiki-init.service" ];
      path = [ pkgs.postfix ];
      description = "KN Daan";
      environment = config.kn.shared.env // {
        KN_LDAP_USER = cfg.ldap.user;
        KN_LDAP_PASS = cfg.ldap.pass;
      };
      preStart = "mkdir -p /var/lib/postfix/conf/virtual";
      serviceConfig = {
        ExecStart = "${pkgs.kninfra}/utils/daan.py";
        Restart = "on-failure";
        # SupplementaryGroups = "infra";
        Type = "notify";
        NotifyAccess = "all";
      };
    };
  };
}


  
