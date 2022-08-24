# The module containing the django configuration
# this is enabled with kn.django.enable = true;
# it configures nginx, mongo and an uwsgi systemd service
{ config, lib, pkgs, ... }:
let
  cfg = config.kn.shared;
  # generate a json file with configuration for uwsgi
  kn_env = config.kn.shared.env;
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
      # GRPC_VERBOSITY="DEBUG";
      # GRPC_TRACE="tcp";
    };
    # TODO: limit access to mongodb
    services.mongodb.enable = true;
    users.groups.infra = {};
    # socket activation
    environment.systemPackages = [(
      pkgs.runCommandNoCC "knshell" { buildInputs = [ pkgs.makeWrapper ]; } ''
        makeWrapper ${pkgs.kninfra}/bin/shell $out/bin/knshell \
        ${lib.concatStringsSep " " (lib.mapAttrsToList (n: v: ''--set "${n}" "${v}"'') kn_env)}
      ''
    )];
    # create /var/photos directory
    systemd.tmpfiles.rules = [
      "d /var/fotos 0550 root infra -"
    ];
    systemd.services = lib.mkIf cfg.initialDB {
      giedo = rec {
        requires = [ "kn_initial_state.service" ];
        after = requires;
        serviceConfig.EnvironmentFile = config.age.secrets.kn-env.path;
      };
      kndjango = rec {
        requires = [ "kn_initial_state.service" ];
        after = requires;
        serviceConfig.EnvironmentFile = config.age.secrets.kn-env.path;
      };
      rimapd = rec {
        requires = [ "kn_initial_state.service" ];
        after = requires;
        #serviceConfig.EnvironmentFile = config.age.secrets.kn-env.path;
      };
      hans.serviceConfig.EnvironmentFile = config.age.secrets.kn-env.path;
      kn_initial_state = rec {
        requires = [ "mongodb.service" ];
        after = requires;
        serviceConfig = {
          StateDirectory = "kndjango";
          Type = "oneshot";
          RemainAfterExit = true;
        };
        script = ''
          # initialize the DB if this has not happened before
          if [ ! -f /var/lib/kndjango/database-initialized ]; then
            ${pkgs.kninfra}/libexec/initializeDb.py
            touch /var/lib/kndjango/database-initialized
          fi
        '';
      };
    };
  };
}
