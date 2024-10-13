# The module containing the django configuration
# this is enabled with kn.django.enable = true;
# it configures nginx, mongo and an uwsgi systemd service
{ config, lib, pkgs, ... }:
let
  cfg = config.kn.shared;

  knshell = pkgs.runCommandNoCC "knshell" { buildInputs = [ pkgs.makeWrapper ]; } ''
    makeWrapper ${pkgs.kninfra}/bin/shell $out/bin/knshell \
    ${lib.concatStringsSep " " (lib.mapAttrsToList (n: v: ''--set "${n}" "${v}"'') cfg.env)}
  '';

in {
  options.kn.shared = with lib; {
    enable = mkEnableOption "KN DB";
    initialDB = mkOption {
      type = types.bool;
    };
    env = mkOption {
      type = types.attrsOf types.str;
      default = {};
    };
  };
  config = lib.mkIf cfg.enable {
    kn.shared.env = {
      DJANGO_SETTINGS_MODULE = "kn.settings_env";
      KN_GIEDO_SOCKET = config.kn.giedo.socket;
      KN_SETTINGS = "${config.kn.settingsFile}";
      # GRPC_VERBOSITY="DEBUG";
      # GRPC_TRACE="tcp";
    };
    services.mongodb.enable = true;
    services.mongodb.bind_ip = "/run/mongodb/mongodb.sock";
    users.groups.infra = {};
    environment.systemPackages = [ pkgs.mongosh knshell ];
    systemd.services = lib.mkMerge [
      {
        mongodb.serviceConfig.RuntimeDirectory = "mongodb";
        mongodb.postStart = ''
          chmod g+rw /run/mongodb/mongodb.sock
        '';
      }
      (lib.mkIf cfg.initialDB {
        kn_initial_state = rec {
          requires = [ "mongodb.service" ];
          after = requires;
          requiredBy = [ "giedo.service" "kndjango.service" "rimapd.service" ];
          before = requiredBy;
          serviceConfig = {
            StateDirectory = "kndjango";
            Type = "oneshot";
            RemainAfterExit = true;
            EnvironmentFile = config.age.secrets.kn-env.path;
          };
          script = ''
            # initialize the DB if this has not happened before
            if [ ! -f /var/lib/kndjango/database-initialized ]; then
              ${pkgs.kninfra}/libexec/initializeDb.py
              touch /var/lib/kndjango/database-initialized
            fi
          '';
        };
        kn_initial_sync = rec {
          requires = [ "giedo.service" "hans.service" "daan.service" ];
          after = requires;
          wantedBy = [ "multi-user.target" ];
          serviceConfig = {
            Type = "oneshot";
            RemainAfterExit = true;
            EnvironmentFile = config.age.secrets.kn-env.path;
            ExecStart = "${pkgs.kninfra}/utils/giedo-sync.py";
          };
          environment = cfg.env;
        };
      })
    ];
  };
}
