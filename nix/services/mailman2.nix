
{ config, lib, pkgs, ... }:
let cfg = config.services.mailman2;
    cgi = [
      "admin"
      "admindb"
      "confirm"
      "create"
      "edithtml"
      "listinfo"
      "options"
      "private"
      "rmlist"
      "roster"
      "subscribe"
    ];
in {
  options.services.mailman2 = with lib; {
    enable = mkEnableOption "mailman";
    user = mkOption {
      type = types.str;
      default = "list";
    };
  };
  # TODO: use upstream mailman module
  config = lib.mkIf cfg.enable {
    users.users.list = {
      name = cfg.user;
      uid = 316; # see misc/ids.nix
      home = "/var/lib/mailman";
      isSystemUser = true;
    };
    users.groups.mailman = {};
    systemd.tmpfiles.rules = lib.mkIf cfg.enable [
      "d /var/lib/mailman 02775 ${cfg.user} mailman -"
      "d /var/lib/mailman/lists 02775 ${cfg.user} mailman -"
      "d /var/lib/mailman/data 02775 ${cfg.user} mailman -"
      "d /var/lib/mailman/qfiles 02770 ${cfg.user} mailman -"
      "d /var/lib/mailman/archives 02775 ${cfg.user} mailman -"
      "d /var/lib/mailman/archives/public 02775 ${cfg.user} mailman -"
      "d /var/lib/mailman/archives/private 02770 ${cfg.user} mailman -"
      "d /var/lib/mailman/logs 02775 ${cfg.user} mailman -"
      "d /var/lib/mailman/locks 02775 ${cfg.user} mailman -"
      "d /var/lib/mailman/spam 02775 ${cfg.user} mailman -"
    ];

    # systemd.services.mailman = {
      
    # };
    environment.etc."mailman_cfg.py".text = ''
      from Defaults import *

      # TODO https
      DEFAULT_URL_PATTERN = 'https://%s/mailman/'
      IMAGE_LOGOS = '/mailman-icons/'

      MAILMAN_USER = "list"
      MAILMAN_GROUP = "mailman"
      
      DEFAULT_EMAIL_HOST = 'lists.${config.networking.domain}'
      DEFAULT_URL_HOST = '${config.networking.domain}'
      
      add_virtualhost(DEFAULT_URL_HOST, DEFAULT_EMAIL_HOST)
      
      DEFAULT_SERVER_LANGUAGE = 'en'
      USE_ENVELOPE_SENDER = 0
      DEFAULT_SEND_REMINDERS = 0
      MTA = 'Postfix'
      POSTFIX_STYLE_VIRTUAL_DOMAINS = ['lists.${config.networking.domain}']
      VIRTUAL_HOST_OVERVIEW = Off
      DEB_LISTMASTER = 'wortel@${config.networking.domain}'
      DEFAULT_LIST_ADVERTISED = False
    '';
    services.nginx.enable = true;
    services.nginx.virtualHosts.kn = {
      locations."/mailman-icons/".alias =
        "${pkgs.mailman2}/icons/";
      locations."~ ^/mailman(/[^/]+)(/.+)?$" = {
        # mailman wants to be setgid 'mailman'
        root = pkgs.linkFarm "mailman-cgi-bin" (lib.flip map cgi (name:
          { inherit name; path = "/run/wrappers/bin/mailman-${name}-cgi"; }
        ));
        extraConfig = ''
          fastcgi_pass unix:${config.services.fcgiwrap.socketAddress};
          fastcgi_read_timeout 720;
          fastcgi_param PATH_INFO $2;
          fastcgi_param SCRIPT_FILENAME $document_root$1;
          include ${pkgs.nginx}/conf/fastcgi_params;
          #include ${pkgs.nginx}/conf/fastcgi.conf;
        '';
      };
    };
    security.wrappers = lib.listToAttrs (lib.flip map cgi (name: {
      name = "mailman-${name}-cgi";
      value = {
        source = "${pkgs.mailman2}/cgi-bin/${name}";
        setgid = true;
        group = "mailman";
      };
    })) // {
      mailman-mailman-mail = {
        source = "${pkgs.mailman2}/mail/mailman";
        setgid = true;
        group = "mailman";
      };
    };
    users.groups.cgi = {};
    services.fcgiwrap = {
      enable = true;
      user = "nginx";
      group = "cgi";
    };
  };
}
