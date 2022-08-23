# The module containing the django configuration
# this is enabled with kn.django.enable = true;
# it configures nginx, mongo and an uwsgi systemd service
{ config, lib, pkgs, ... }:
let
  cfg = config.kn.django;
  # generate a json file with configuration for uwsgi
  kn_env = config.kn.shared.env // {
    KN_ALLOWED_HOSTS =
      "${config.services.nginx.virtualHosts.kn.serverName}";
  };
  uswgi_conf = pkgs.writeText "uwsgi.json" (builtins.toJSON {
    uwsgi = {
      plugins = "python3";
      chdir = pkgs.kninfra;
      module = "kn.wsgi";
      master = true;
      enable_threads = true;
      env = [
        "PYTHONPATH=${pkgs.kninfra.PYTHONPATH}"
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
    kn.shared.enable = true;
    services.nginx = {
      enable = true;
      virtualHosts.kn = {
        locations."/djmedia/".alias = "${pkgs.kninfra}/media/";
        locations."/".extraConfig = ''
          include ${pkgs.nginx}/conf/uwsgi_params;
          uwsgi_pass unix:${config.kn.django.socket};
         '';
      };
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
      requires = [ "mongodb.service" ];
      after = requires;
      environment = kn_env;
      # todo: should this be here?
      path = [ (lib.getBin pkgs.imagemagick) ];
      serviceConfig = {
        ExecStart = "${uwsgi_pkg}/bin/uwsgi --json ${uswgi_conf}";
        # allocate a dynamic user for every run. maximum sandboxing
        DynamicUser = true;
        CacheDirectory = "fotos";
        Restart = "on-failure";
        KillSignal = "SIGQUIT";
        SupplementaryGroups = "infra";
        # uwsgi is systemd-aware
        Type = "notify";
        NotifyAccess = "all";
      };
    };
    # create /var/photos directory
    systemd.tmpfiles.rules = [
      "d /var/fotos 0550 root infra -"
    ];
  };
}
