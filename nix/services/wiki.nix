{ config, lib, pkgs, ... }:
let cfg = config.kn.wiki;
in {
  options.kn.wiki.enable = lib.mkEnableOption "wiki";
  config = lib.mkIf cfg.enable {
    services.nginx.enable = true;
    services.nginx.virtualHosts."kn" = {
      locations."/wiki/".extraConfig = ''
        rewrite ^/wiki/([^\?]*) /W/index.php?title=$1&$args;
      '';
      locations."/wiki".extraConfig = ''
        rewrite ^/wiki /W/index.php;
      '';
      locations."/W" = {
        alias = "${pkgs.mediawiki}/share/mediawiki";
        index = "index.html index.php";
      };
      # We would like to write this as a .php block within the previous
      # location block, but then we run into the following nginx bug
      #  http://trac.nginx.org/nginx/ticket/97
      locations."~ ^/W(/.+.php)$" = {
        alias = "${pkgs.mediawiki}/share/mediawiki$1";
        extraConfig = ''
          if (!-f ${pkgs.mediawiki}/share/mediawiki$1) { return 404; }

          fastcgi_param SCRIPT_FILENAME $document_root$1;
          fastcgi_index index.php;
          fastcgi_read_timeout 720;
          fastcgi_pass unix:${config.services.phpfpm.pools.mediawiki.socket};
          include ${pkgs.nginx}/conf/fastcgi_params;
        '';
      };
    };
    services.mediawiki = {
      enable = true;
      # httpd = "nginx"; # TODO
      database.type = "postgres";
    };
  };
}
