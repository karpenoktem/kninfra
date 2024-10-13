# The module containing the django configuration
# this is enabled with kn.django.enable = true;
# it configures nginx, mongo and an uwsgi systemd service
{ config, lib, pkgs, ... }:
let
  cfg = config.kn.django;
  # generate a json file with configuration for uwsgi
  kn_env = config.kn.shared.env;
  uswgi_conf = pkgs.writeText "uwsgi.json" (builtins.toJSON {
    uwsgi = {
      plugins = "python3";
      chdir = cfg.package;
      module = "kn.wsgi";
      master = true;
      enable_threads = true;
      env = [
        "PYTHONPATH=${pkgs.kninfra.PYTHONPATH}"
      ];
    };
  });
  # customize the uwsgi package to have python3 support
  uwsgi_pkg = pkgs.uwsgi.override {
    plugins = [ "python3" ];
    python3 = pkgs.python3-kn;
  };
in {
  # defining the kn.django config settings
  options.kn.django = with lib; {
    enable = mkEnableOption "KN website";
    socket = mkOption {
      default = "/run/infra/S-django";
      description = "The socket path to use for UWSGI";
      type = types.path;
    };
    package = mkOption {
      description = "The kninfra package to use";
      default = pkgs.kninfra;
      defaultText = "pkgs.kninfra";
      type = types.path;
    };
    serveMediaUsingNginx = mkOption {
      # doesn't work in VM :(
      description = ''
        Use nginx to serve media directory.
      '';
      default = true;
      type = types.bool;
    };
  };
  config = lib.mkIf cfg.enable {
    kn.shared.enable = true;
    services.nginx = {
      enable = true;
      virtualHosts.kn = lib.mkMerge [
        {
          serverName = config.kn.settings.DOMAINNAME;
          locations."/".extraConfig = ''
            include ${pkgs.nginx}/conf/uwsgi_params;
            uwsgi_pass unix:${config.kn.django.socket};
          '';
        }
        {
          locations = lib.mkIf cfg.serveMediaUsingNginx {
            "/djmedia/".alias = "${cfg.package}/media/";
          };
        }
      ];
    };
    systemd.sockets.kndjango = {
      wantedBy = [ "sockets.target" ];
      listenStreams = [ config.kn.django.socket ];
      socketConfig = {
        SocketGroup = "nginx";
        SocketUser = "nginx";
        SocketMode = "0660";
      };
    };

    users.groups.kndjango = { };
    users.users.kndjango = {
      isSystemUser = true;
      group = "kndjango";
    };

    systemd.services.kndjango = rec {
      requires = [ "mongodb.service" ];
      after = requires;
      environment = kn_env;
      # todo: should this be here?
      path = [ (lib.getBin pkgs.imagemagick) ];
      serviceConfig = {
        ExecStart = "${uwsgi_pkg}/bin/uwsgi --json ${uswgi_conf}";
        DynamicUser = true;
        User = "kndjango";
        Group = "kndjango";
        SupplementaryGroups = [ "fotos" "infra" "mongodb" ];
        ReadWritePaths = [ config.kn.fotos.dir ];
        CacheDirectory = "fotos";
        Restart = "on-failure";
        KillSignal = "SIGQUIT";
        # uwsgi is systemd-aware
        Type = "notify";
        NotifyAccess = "all";
        EnvironmentFile = config.age.secrets.kn-env.path;
      };
    };
  };
}
