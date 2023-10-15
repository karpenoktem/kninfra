{ config, lib, pkgs, ... }:

let
  cfg = config.kn.wiki;
  knVhost = config.services.nginx.virtualHosts.kn;
  wgVerifyHost = "http${lib.optionalString knVhost.forceSSL "s"}://${knVhost.serverName}";

  package = pkgs.stdenv.mkDerivation rec {
    pname = "mediawiki-full";
    version = src.version;
    src = pkgs.mediawiki;

    installPhase = ''
      mkdir -p $out
      cp -r * $out/

      rm -rf $out/share/mediawiki/skins/*
      rm -rf $out/share/mediawiki/extensions/*

      ${lib.concatStringsSep "\n" (lib.mapAttrsToList (k: v: ''
        ln -s ${v} $out/share/mediawiki/skins/${k}
      '') config.services.mediawiki.skins)}

      ${lib.concatStringsSep "\n" (lib.mapAttrsToList (k: v: ''
        ln -s ${if v != null then v else "$src/share/mediawiki/extensions/${k}"} $out/share/mediawiki/extensions/${k}
      '') config.services.mediawiki.extensions)}
    '';
  };

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
      locations."/W/" = {
        alias = "${package}/share/mediawiki/";
        index = "index.html index.php";
      };
      # We would like to write this as a .php block within the previous
      # location block, but then we run into the following nginx bug
      #  http://trac.nginx.org/nginx/ticket/97
      locations."~ ^/W(/.+.php)$" = {
        alias = "${package}/share/mediawiki$1";
        extraConfig = ''
          if (!-f ${package}/share/mediawiki$1) { return 404; }

          fastcgi_param SCRIPT_FILENAME $document_root$1;
          fastcgi_index index.php;
          fastcgi_read_timeout 720;
          fastcgi_pass unix:${config.services.phpfpm.pools.mediawiki.socket};
          include ${pkgs.nginx}/conf/fastcgi_params;
        '';
      };
    };
    services.mysql.ensureUsers = [
      {
        name = "giedo";
        ensurePermissions = {
          "mediawiki.*" = "SELECT";
        };
      }
    ];
    services.mediawiki = {
      enable = true;
      name = "KnWiki";
      # TODO: use this module to host this on nginx
      # httpd = "nginx"; # TODO
      database.createLocally = true;
      #database.type = "postgres";
      virtualHost = {
        hostName = "localhost:8080";
        enableSSL = false;
        adminAddr = "yorick@yori.cc";
      };
      extraConfig = let
        extensions.Auth_remoteuser = pkgs.fetchFromGitHub {
          owner = "wikimedia";
          repo = "mediawiki-extensions-Auth_remoteuser";
          rev = "cf8b45eea7520631efeb1e5055c16ee960bc798a";
          sha256 = "sha256-2mww+PAurdWuLom29ePbpbqq9BlQSWsxtbN1yiV4UxM=";
        };
        in ''
        // $wgDebugLogFile = "/tmp/debug-mediawiki.log";
        $wgScriptPath       = "/W";
        $wgArticlePath      = "/wiki/$1";
        $wgResourceBasePath = $wgScriptPath;
        $wgEnableEmail      = false; # TODO
        $wgEnableUserEmail  = true; # UPO

        $wgUsePathInfo      = true;
        $wgScriptExtension  = ".php";
        $wgStylePath        = "$wgScriptPath/skins";


        //$wgEmergencyContact = "webcie@{{ grains['fqdn'] }}";
        //$wgPasswordSender   = "root@{{ grains['fqdn'] }}";

        $wgEnotifUserTalk      = false;
        $wgEnotifWatchlist     = false;
        $wgEmailAuthentication = true;

        $wgFileExtensions = array( 'png', 'gif', 'jpg', 'jpeg', 'pdf' );

        $wgMainCacheType    = CACHE_ACCEL;

        $wgEnableUploads  = true;

        $wgUseInstantCommons  = false;
        $wgShellLocale = "en_US.utf8";

        $wgLanguageCode = "nl";

        $wgRightsPage = "";
        $wgRightsUrl  = "";
        $wgRightsText = "";
        $wgRightsIcon = "";

        $wgResourceLoaderMaxQueryLength = -1;

        $wgGroupPermissions['*']['autocreateaccount'] = false;
        $wgGroupPermissions['*']['createaccount'] = true;
        $wgGroupPermissions['*']['edit'] = false;
        $wgGroupPermissions['*']['read'] = false;
        $wgGroupPermissions['webcie']['delete'] = true;
        $wgGroupPermissions['webcie']['undelete'] = true;
        $wgGroupPermissions['webcie']['browsearchive'] = true;
        $wgGroupPermissions['webcie']['deletedhistory'] = true;

        $wgLogo             = "/djmedia/base/wiki-logo.png";
        # TODO
        # $wgUsersNotifiedOnAllChanges = array('Bas', 'Bramw');
        $wgGroupPermissions['user']['createaccount'] = false;
        $wgGroupPermissions['leden'] = $wgGroupPermissions['user'];
        $wgGroupPermissions['user']['edit'] = false;
        $wgGroupPermissions['user']['read'] = false;
        $wgUseRCPatrol = false;
        $wgGroupPermission['sysop']['patrol'] = false;
        # TODO
        # require_once($IP ."/extensions/APC/APC.php");
        # $wgGroupPermissions['sysop']['apc'] = true;
        $wgAllowExternalImagesFrom = array('https://nirodha.karpenoktem.nl/');
        
        // TODO, only in VM
        //{% if grains['vagrant'] %}
        $wgShowExceptionDetails = true;
        //{% endif %}
        
        $wgKNAuthVerifyURL = '${wgVerifyHost}/accounts/api/';
        wfLoadExtension("Auth_remoteuser", "${extensions.Auth_remoteuser}/extension.json");
        include "${./knauth.php}";
      '';
      passwordFile = pkgs.writeText "mediawiki-password" "0e6hW5br5ecUjvcI";
    };
    services.httpd = {
      enable = lib.mkForce false;
      user = "nginx";
      group = "nginx";
    };
    services.phpfpm.phpOptions = ''
      extension=${pkgs.phpExtensions.apcu}/lib/php/extensions/apcu.so
    '';
  };
}
