# The module containing the django configuration
# this is enabled with kn.django.enable = true;
# it configures nginx, mongo and an uwsgi systemd service
{ config, lib, pkgs, ... }:
let
  cfg = config.kn.django;
  # generate a json file with configuration for uwsgi
  kn_env = {
    DJANGO_SETTINGS_MODULE = "kn.settings_env";
    KN_GIEDO_SOCKET = config.kn.giedo.socket;
    KN_HANS_SOCKET = config.kn.hans.socket;
    KN_SECRET_KEY = "CHANGE ME";
    KN_CHUCK_NORRIS_HIS_SECRET = "CHANGE ME";
    # GRPC_VERBOSITY="DEBUG";
    # GRPC_TRACE="tcp";
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
  options.kn.giedo = with lib; {
    enable = mkEnableOption "KN Giedo";
    socket = mkOption {
      default = "/run/infra/giedo";
      description = "The socket path to use for Giedo";
      type = types.path;
    };
  };
  options.kn.hans = with lib; {
    enable = mkEnableOption "KN Hans";
    socket = mkOption {
      default = "/run/infra/hans";
      description = "The socket path to use for Hans";
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
    users.groups.infra = {};
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
      requires = [ "mongodb.service" "kn_initial_state.service" ];
      after = requires;
      environment = kn_env;
      path = [ "${lib.getBin pkgs.imagemagick}/bin" ];
      serviceConfig = {
        ExecStart = "${pkgs.kninfra}/utils/giedo.py";
        DynamicUser = true;
        Restart = "on-failure";
        SupplementaryGroups = "infra";
        Type = "notify";
        NotifyAccess = "all";
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
    systemd.sockets.hans = {
      wantedBy = [ "sockets.target" ];
      listenStreams = [ config.kn.hans.socket ];
      socketConfig = {
        SocketGroup = "infra";
        SocketMode = "0660";
      };
    };
    systemd.services.hans = rec {
      requires = [ "kn_initial_state.service" ]; # todo: mailman
      after = requires;
      environment = kn_env // {
        KN_MAILMAN_PATH = pkgs.mailman2;
      };
      serviceConfig = {
        ExecStart = "${pkgs.kninfra}/bin/hans";
        User = config.services.mailman2.user;
        Restart = "on-failure";
        Type = "notify";
        SupplementaryGroups = "infra"; # todo: reason about security
        NotifyAccess = "all";
      };
    };
    environment.systemPackages = [(
      pkgs.runCommandNoCC "knshell" { buildInputs = [ pkgs.makeWrapper ]; } ''
        makeWrapper ${pkgs.kninfra}/utils/scan-fotos.py $out/bin/kn-scan-fotos \
        ${lib.concatStringsSep " " (lib.mapAttrsToList (n: v: ''--set "${n}" "${v}"'') kn_env)}
        makeWrapper ${pkgs.kninfra}/bin/shell $out/bin/knshell \
        ${lib.concatStringsSep " " (lib.mapAttrsToList (n: v: ''--set "${n}" "${v}"'') kn_env)}
      ''
    )];
    systemd.services.kndjango = rec {
      requires = [ "mongodb.service" "kn_initial_state.service" ];
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
    systemd.services.kn_initial_state = rec {
      requires = [ "mongodb.service" ];
      after = requires;
      serviceConfig = {
        StateDirectory = "kndjango";
        Type = "oneshot";
        RemainAfterExit = true;
      };
      script = ''
        # initialize the DB if this has not happened before
        # TODO: only in VM
        if [ ! -f /var/lib/kndjango/database-initialized ]; then
          ${pkgs.kninfra}/libexec/initializeDb.py
          touch /var/lib/kndjango/database-initialized
        fi
      '';
    };
  };
}
