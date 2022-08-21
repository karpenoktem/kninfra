{ config, lib, pkgs, ... }:
let
  cfg = config.kn.giedo;
  kn_env = config.kn.shared.env;
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
    ldap.user = mkOption {
      type = types.str;
    };
    # todo: remove
    ldap.pass = mkOption {
      type = types.str;
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
        KN_LDAP_USER = "cn=infra,dc=karpenoktem,dc=nl"; # TODO suffix
        KN_LDAP_PASS = "CHANGE ME";
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
        SupplementaryGroups = "infra";
        Type = "notify";
        NotifyAccess = "all";
      };
    };
    environment.systemPackages = [(
      pkgs.runCommandNoCC "kngiedo" { buildInputs = [ pkgs.makeWrapper ]; } ''
        makeWrapper ${pkgs.kninfra}/utils/scan-fotos.py $out/bin/kn-scan-fotos \
        ${lib.concatStringsSep " " (lib.mapAttrsToList (n: v: ''--set "${n}" "${v}"'') kn_env)}
        makeWrapper ${pkgs.kninfra}/utils/giedo-sync.py $out/bin/kn-giedo-sync \
        ${lib.concatStringsSep " " (lib.mapAttrsToList (n: v: ''--set "${n}" "${v}"'') kn_env)}
      ''
    )];
  };
}
