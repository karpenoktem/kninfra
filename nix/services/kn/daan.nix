{ pkgs, lib, config, ... }:

let cfg = config.kn.daan;

in {
  options.kn.daan = with lib; {
    enable = mkEnableOption "KN Daan";
    socket = mkOption {
      default = "/run/infra/daan";
      description = "The socket path to use for Daan";
      type = types.path;
    };

    postfixMapDir = mkOption {
      type = types.path;
      default = "/var/lib/postfix/conf/virtual";
      description = ''
        Directory where daan will write generated maps for postfix to use.
      '';
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
      preStart = "mkdir -p ${cfg.postfixMapDir}";

      environment = {
        POSTFIX_VIRTUAL_MAP = "${cfg.postfixMapDir}/kninfra_maps";
        POSTFIX_SLM_MAP = "${cfg.postfixMapDir}/kninfra_slm_maps";
        PHOTOS_DIR = config.kn.fotos.dir;
      };

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
