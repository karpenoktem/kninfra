{ config, lib, pkgs, ... }:
let
  cfg = config.kn.hans;
in {
  options.kn.hans = with lib; {
    enable = mkEnableOption "KN Hans";
    socket = mkOption {
      default = "/run/infra/hans";
      description = "The socket path to use for Hans";
      type = types.path;
    };
  };
  config = lib.mkIf cfg.enable {
    users.groups.infra = {};
    # socket activation
    systemd.sockets.hans = {
      wantedBy = [ "sockets.target" ];
      listenStreams = [ cfg.socket ];
      socketConfig = {
        SocketGroup = "infra";
        SocketMode = "0660";
      };
    };
    systemd.services.hans = {
      environment = config.kn.shared.env;
      serviceConfig = {
        ExecStart = "${pkgs.kninfra}/utils/hans.py";
        User = "mailman";
        Restart = "on-failure";
        Type = "notify";
        NotifyAccess = "all";
        EnvironmentFile = config.age.secrets.kn-env.path;
      };
    };
  };
}
