{ config, lib, pkgs, ... }:
let
  cfg = config.kn.hans;
  # generate a json file with configuration for uwsgi
  kn_env = config.kn.shared.env;
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
      environment = kn_env // {
        KN_MAILMAN_PATH = pkgs.mailman2;
        KN_MAILMAN_DEFAULT_PASSWORD = "asdf";
      };
      serviceConfig = {
        ExecStart = "${pkgs.kninfra}/bin/hans";
        User = config.services.mailman2.user;
        Restart = "on-failure";
        Type = "notify";
        NotifyAccess = "all";
      };
    };
  };
}
