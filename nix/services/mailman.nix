
{ config, lib, pkgs, ... }:
let cfg = config.services.mailman2;
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
    systemd.tmpfiles.rules = lib.mkIf cfg.enable [
      "d /var/lib/mailman 700 ${cfg.user} nogroup -"
    ];

    # systemd.services.mailman = {
      
    # };
    services.nginx.enable = true;
    services.nginx.virtualHosts.kn = {
      locations."/mailman-icons/".alias =
        "${pkgs.mailman2}/icons/";
      locations."~ ^/mailman(/[^/]+)(/.+)?$" = {
        root = "${pkgs.mailman2}/cgi-bin";
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
    services.fcgiwrap.enable = true;
  };
}
