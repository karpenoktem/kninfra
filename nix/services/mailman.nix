{ config, lib, pkgs, ... }:
let cfg = config.kn.mailman;
in {
  options.kn.mailman.enable = lib.mkEnableOption "mailman";
  # TODO: use upstream mailman module
  config = lib.mkIf cfg.enable {
    services.nginx.enable = true;
    services.nginx.virtualHosts.kn = {
      locations."/mailman-icons".alias =
        "${pkgs.python3Packages.mailman-web}/icons";
      locations."~ ^/mailman(/[^/]+)(/.+)?$" = {
        root = "${pkgs.python3Packages.mailman-web}/cgi-bin";
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
