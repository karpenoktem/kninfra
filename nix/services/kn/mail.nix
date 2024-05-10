{ config, lib, pkgs, ... }:

let
  cfg = config.kn.mailserver;
  certDir = config.security.acme.certs.${cfg.hostname}.directory;

in {
  options.kn.mailserver = with lib; {
    enable = mkEnableOption "mailserver";
    domain = mkOption { default = "karpenoktem.nl"; };
    hostname = mkOption { default = "vipassana.karpenoktem.nl"; };
  };

  config = lib.mkIf cfg.enable {
    security.acme.certs.${cfg.hostname}.group = "postfix";

    services.postfix = {
      enable = true;
      domain = cfg.domain;
      rootAlias = "wortel@${cfg.domain}";
      postmasterAlias = "root";
      extraAliases = ''
        logcheck: root
        devnull: /dev/null
      '';

      hostname = cfg.hostname;
      origin = "$mydomain";
      recipientDelimiter = "+";
      relayDomains = [
        "lists.karpenoktem.nl"
        "hash:/var/lib/mailman/data/postfix_domains"
      ];
      destination = [ "$myhostname" "localhost" "local.${cfg.domain}" ];

      sslCert = "${certDir}/cert.pem";
      sslKey = "${certDir}/key.pem";

      # main.cf
      config = {
        # appending .domain is the MUA's job
        append_dot_mydomain = false;
        biff = false;
        broken_sasl_auth_clients = true;
        recipient_bcc_maps = "hash:/etc/postfix/recipient_bcc_maps";

        smtpd_tls_CAfile = config.services.postfix.tlsTrustedAuthorities;

        smtpd_banner = "$myhostname ESMTP NO UCE";
        smtpd_helo_required = true;

        smtpd_sender_restrictions = [
          "check_sender_access hash:/etc/postfix/sender_access"
          "reject_unknown_sender_domain"
          "permit_mynetworks"
          "reject_sender_login_mismatch"
        ];

        mydestination = [ "$myhostname" "localhost" "local.karpenoktem.nl" ];

        mynetworks = [ "127.0.0.0/8" "[::ffff:127.0.0.0]/104" "[::1]/128" ];

        # opendkim
        # smtpd_milters = [ "inet:localhost:11332" "inet:localhost:8891" ];
        # non_smtpd_milters = "inet:localhost:8891";

        # sender_canonical_maps = "pcre:/etc/postfix/sender_canonical_map";
        # smtp_sasl_password_maps = "hash:/etc/postfix/sasl_passwd";

        smtp_tls_session_cache_database =
          "btree:\${data_directory}/smtp_scache";

        smtpd_sender_login_maps =
          "hash:${config.kn.daan.postfixMapDir}/kninfra_slm_maps";

        smtpd_tls_session_cache_database =
          "btree:\${data_directory}/smtpd_scache";
        virtual_alias_domains = [
          "lists.kn.cx"
          "kn.cx"
          "karpenoktem.nl"
          "zeusverbond.nl"
          "karpenoktem.com"
          "lists.karpenoktem.com"
          "dispuutcoma.nl"
        ];

        virtual_alias_maps = [
          "hash:/var/lib/postfix/conf/virtual_pre_map"
          "hash:${config.kn.daan.postfixMapDir}/kninfra_maps"
          "hash:/var/lib/postfix/conf/virtual_post_map"
        ];

        disable_vrfy_command = true;
        mailbox_size_limit = "0"; # defaults to 51200000
        message_size_limit = "51200000"; # defaults to 10240000
        smtp_sasl_auth_enable = true;
        # defaults to noplaintext,noanonymous
        smtp_sasl_tls_security_options = "noanonymous";
        smtpd_tls_ciphers = "high";
        smtpd_sasl_auth_enable = true;
        smtpd_sasl_authenticated_header = true;
        smtpd_sasl_local_domain = "";
        #cyrus_sasl_config_path = /etc/postfix/sasl
        local_recipient_maps = [ "hash:/var/lib/mailman/data/postfix_lmtp" ];

        smtpd_recipient_restrictions = [
          "permit_mynetworks"
          "warn_if_reject reject_authenticated_sender_login_mismatch"
          "permit_sasl_authenticated"
          "reject_unauth_destination"
          "reject_unauth_pipelining"
          "reject_non_fqdn_helo_hostname"
          "reject_invalid_helo_hostname"
          "reject_unknown_recipient_domain"
          "reject_unknown_helo_hostname"
          #"reject_rbl_client zen.spamhaus.org"
          #"reject_rbl_client cbl.abuseat.org"
          "permit"
        ];

        smtpd_relay_restrictions = [
          "permit_mynetworks"
          "reject_authenticated_sender_login_mismatch"
          "permit_sasl_authenticated"
          "reject_unauth_destination"
          "permit"
        ];
      };

      config.transport_maps = [ "hash:/var/lib/mailman/data/postfix_lmtp" ];

      mapFiles.recipient_bcc_maps =
        pkgs.writeText "postfix-recipient-bcc-maps" ''
          voorzitter@${cfg.domain}  secretaris@${cfg.domain}
        '';

      mapFiles.virtual_pre_map = pkgs.writeText "virtual-pre-map" ''
        leden@dispuutcoma.nl coma@karpenoktem.nl
        beekmans@dispuutcoma.nl stan@karpenoktem.nl

        postmaster@dispuutcoma.nl wortel@karpenoktem.nl
        wortel@dispuutcoma.nl wortel@karpenoktem.nl
        abuse@dispuutcoma.nl wortel@karpenoktem.nl
      '';
      mapFiles.virtual_post_map = pkgs.writeText "virtual-post-map" ''
        root@karpenoktem.nl wortel@karpenoktem.nl
        postmaster@karpenoktem.nl wortel@karpenoktem.nl
        geinteresseerden@karpenoktem.nl geinteresseerden@lists.karpenoktem.nl
        devnull@karpenoktem.nl devnull@localhost
        @karpenoktem.com @karpenoktem.nl
        @kn.cx @karpenoktem.nl
        @lists.karpenoktem.com @lists.karpenoktem.nl
        @lists.kn.cx @lists.karpenoktem.nl
        ; @karpenoktem.nl knfilter@gmail.com
        @karpenoktem.nl catchall@lists.karpenoktem.nl
        postmaster@zeusverbond.nl wortel@karpenoktem.nl
        webmaster@zeusverbond.nl wortel@karpenoktem.nl
        abuse@zeusverbond.nl wortel@karpenoktem.nl
        hostmaster@zeusverbond.nl wortel@karpenoktem.nl
        @sankhara.karpenoktem.nl @karpenoktem.nl
      '';
      # List of addresses to DISCARD due to spam.
      mapFiles.sender_access = pkgs.writeText "postfix-sender_access"
        (lib.concatMapStrings (domain: ''
          ${domain} DISCARD
        '') [
          "admin2@advertise-bz.cn"
          "admin@advertise-bz.cn"
          "bellis.host"
          "beta-training.be"
          "bitmaner.eu"
          "contact@news.offerte-specialist.com"
          "fibrotexe.eu"
          "fiztonsky.es"
          "franks-woerterbuch.de"
          "fyre-tec.com"
          "fz-juelich.de"
          "gatco-inc.com"
          "heractivat-betaal@kpnmail.nl"
          "hostepro.co.ua"
          "hu@data.cn.com"
          "info@jobagent.stepstone.de"
          "klantenservice.nl"
          "ledonline11.com"
          "ledonline8.com"
          "mellingrush.eu"
          "modaitaliana.nl"
          "molingrush.co.ua"
          "morana-rtd.com"
          "myfonts.com"
          "newsletters-no-reply@myfonts.com"
          "nextdoor.nl"
          "o3.email.nextdoor.nl"
          "paysto.co.ua"
          "win-love.biz.ua"
          "winsoker.co.ua"
          "worksolution.co.ua"
        ]);

      enableHeaderChecks = true;

      headerChecks = [
        {
          pattern = "From:.*<[a-z]{7}@.*\\.(eu|ua|us)>$";
          action = "REJECT Looks like spam - please contact us if it isn't.";
        }

        {
          pattern = "From:.*@.*\\.nextdoor\\.nl$";
          action = "REJECT";
        }
      ];
    };

    networking.firewall.allowedTCPPorts = [ 25 587 465 ];

    environment.systemPackages = with pkgs; [ opendkim postfix rspamd ];
  };
}
