{ config, lib, pkgs, ... }:
let
  cfg = config.kn.giedo;
  kn_env = config.kn.shared.env;
  # create a wrapper to set all the environment variables
  # todo: I'd use -P on systemd-run, but it breaks the vm test
  wrapScript = name: script: pkgs.writeShellScript name ''
    set -e
    systemd-run -Gt --wait -p EnvironmentFile=${config.age.secrets.kn-env.path} \
      ${lib.concatStringsSep " " (lib.mapAttrsToList (n: v: ''-E "${n}"="${v}"'') kn_env)} \
      ${script} "$@"
  '';
in {
  options.kn.giedo = with lib; {
    enable = mkEnableOption "KN Giedo";
    socket = mkOption {
      default = "/run/infra/giedo";
      description = "The socket path to use for Giedo";
      type = types.path;
    };
    env = mkOption {
      type = types.attrsOf types.str;
      default = {};
    };
  };
  config = lib.mkIf cfg.enable {
    kn.shared.enable = true;
    users.users.giedo = {
      isSystemUser = true;
      group = "giedo";
    };
    users.groups.giedo = {};
    # socket activation
    systemd.sockets.giedo = {
      wantedBy = [ "sockets.target" ];
      listenStreams = [ config.kn.giedo.socket ];
      socketConfig = {
        SocketGroup = "infra";
        SocketMode = "0660";
      };
    };
    systemd.services.giedo = rec {
      requires = [ "mongodb.service" ];
      after = requires;
      environment = kn_env // cfg.env // {
        KN_DAAN_SOCKET = config.kn.daan.socket;
        KN_HANS_SOCKET = config.kn.hans.socket;
      };
      path = [ "${lib.getBin pkgs.imagemagick}/bin" ];
      serviceConfig = {
        User = "giedo";
        ProtectSystem = "strict";
        ProtectHome = true;
        PrivateTmp = true;
        ProtectDevices = true;
        # todo: more sandboxing
        ReadWritePaths = ["/run/infra"];
        ExecStart = "${pkgs.kninfra}/utils/giedo.py";
        Restart = "on-failure";
        SupplementaryGroups = [ "infra" "mongodb" ];
        Type = "notify";
        NotifyAccess = "all";
        EnvironmentFile = config.age.secrets.kn-env.path;
      };
    };
    environment.systemPackages = [(
      pkgs.runCommandNoCC "kngiedo" { buildInputs = [ pkgs.makeWrapper ]; } ''
        mkdir -p $out/bin
        cp ${wrapScript "kn-scan-fotos" "${pkgs.kninfra}/utils/scan-fotos.py"} $out/bin/kn-scan-fotos
        cp ${wrapScript "kn-giedo-sync" "${pkgs.kninfra}/utils/giedo-sync.py"} $out/bin/kn-giedo-sync
      ''
    )];
  };
}
