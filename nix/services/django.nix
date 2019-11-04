# The module containing the django configuration
# this is enabled with kn.django.enable = true;
# it configures nginx, mongo and an uwsgi systemd service
{ config, lib, pkgs, ... }:
let
  cfg = config.kn.django;
  # generate a json file with configuration for uwsgi
  uswgi_conf = pkgs.writeText "uwsgi.json" (builtins.toJSON {
    uwsgi = {
      plugins = "python3";
      chdir = pkgs.kninfra;
      module = "kn.wsgi";
      master = true;
      enable_threads = true;
      env = [
        "DJANGO_SETTINGS_MODULE=kn.settings"
        "PYTHONPATH=${pkgs.kninfra.PYTHONPATH}"
        "HOME=/var/lib/kndjango"
      ];
    };
  });
  # customize the uwsgi package to have python3 support
  uwsgi_pkg = pkgs.uwsgi.override { plugins = [ "python3" ]; };
in {
  # defining the kn.django config settings
  options.kn.django = with lib; {
    enable = mkEnableOption "KN website";
    socket = mkOption {
      default = "/run/infra/S-django";
      description = "The socket path to use for UWSGI";
      type = types.path;
    };
  };
  config = lib.mkIf cfg.enable {
    services = {
      # TODO: limit access to mongodb
      mongodb.enable = true;
      nginx = {
        enable = true;
        virtualHosts.kn = {
          locations."/djmedia/".alias = "${pkgs.kninfra}/media/";
          locations."/".extraConfig = ''
            include ${pkgs.nginx}/conf/uwsgi_params;
            uwsgi_pass unix:${config.kn.django.socket};
           '';
        };
      };
    };
    # socket activation
    systemd.sockets.kndjango = {
      wantedBy = [ "sockets.target" ];
      listenStreams = [ config.kn.django.socket ];
      socketConfig = {
        SocketGroup = "nginx";
        SocketUser = "nginx";
        SocketMode = "0660";
      };
    };
    systemd.services.kndjango = rec {
      requires = [ "mongodb.service" ];
      after = requires;
      preStart = ''
        # reset the settings file
        # TODO: remove?
        rm -f /var/lib/kndjango/settings.py
        cp ${pkgs.kninfra}/kn/settings.example.py /var/lib/kndjango/settings.py
        # initialize the DB if this has not happened before
        # TODO: only in VM
        if [ ! -f /var/lib/kndjango/database-initialized ]; then
          ${pkgs.kninfra}/libexec/initializeDb.py
          touch /var/lib/kndjango/database-initialized
        fi
      '';
      serviceConfig = {
        ExecStart = "${uwsgi_pkg}/bin/uwsgi --json ${uswgi_conf}";
        # have systemd create and manage /var/lib/kndjango
        StateDirectory = "kndjango";
        # allocate a dynamic user for every run. maximum sandboxing
        DynamicUser = true;
        Restart = "on-failure";
        KillSignal = "SIGQUIT";
        # uwsgi is systemd-aware
        Type = "notify";
        NotifyAccess = "all";
      };
    };
  };
}
