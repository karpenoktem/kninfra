{ config, lib, pkgs, ... }:
let
  cfg = config.kn.rimapd;
  # generate a json file with configuration for uwsgi
  kn_env = config.kn.shared.env;
in {
  options.kn.rimapd = with lib; {
    enable = mkEnableOption "KN rimapd";
    port = mkOption {
      default = 13097;
      type = types.port;
    };
  };
  config = lib.mkIf cfg.enable {
    users.groups.infra = {};
    # socket activation
    systemd.sockets.rimapd = {
      wantedBy = [ "sockets.target" ];
      listenStreams = [ "127.0.0.1:${toString cfg.port}" ];
    };
    systemd.services.rimapd = {
      environment = kn_env;
      serviceConfig = {
        ExecStart = "${pkgs.kninfra}/utils/rimapd.py";
        DynamicUser = true;
        Restart = "on-failure";
        Type = "notify";
        NotifyAccess = "all";
        EnvironmentFile = config.age.secrets.kn-env.path;
      };
    };
  };
}
