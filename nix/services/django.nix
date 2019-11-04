{ config, lib, pkgs, ... }:
let cfg = config.kn.django;
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
    uwsgi-pkg = pkgs.uwsgi.override { plugins = [ "python3" ]; };

in {
  options.kn.django = {
    enable = lib.mkEnableOption "kndjango";
    socket = lib.mkOption {
      default = "/run/infra/S-django";
    };
  };
  config = lib.mkIf cfg.enable {
    services.mongodb = {
      enable = true;
    };
    services.nginx.enable = true;
    services.nginx.virtualHosts.kn = {
      locations."/djmedia/".alias = "${pkgs.kninfra}/media/";
      locations."/".extraConfig = ''
        include ${pkgs.nginx}/conf/uwsgi_params;
        uwsgi_pass unix:${config.kn.django.socket};
      '';
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
    systemd.services.kndjango = rec {
      after = requires;
      requires = [ "mongodb.service" ];
      preStart = ''
        rm -f /var/lib/kndjango/settings.py
        cp ${pkgs.kninfra}/kn/settings.example.py /var/lib/kndjango/settings.py
      '';
      serviceConfig = {
        StateDirectory = "kndjango";
        DynamicUser = true;
        Restart = "on-failure";
        KillSignal = "SIGQUIT";
        Type = "notify";
        NotifyAccess = "all";
        ExecStart = "${uwsgi-pkg}/bin/uwsgi --json ${uswgi_conf}";
      };
    };
  };
}
