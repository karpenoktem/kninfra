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
      requires = [ "postfix.service" ];
      after = requires ++ [ "mediawiki-init.service" ];
      path = [ pkgs.postfix ];
      description = "KN Daan";
      environment = config.kn.shared.env;
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


  
