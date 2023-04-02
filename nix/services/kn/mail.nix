{ config, lib, pkgs, ... }:

let cfg = config.kn.mailserver;

in {
  options.kn.mailserver = with lib; {
    enable = mkEnableOption "mailserver";
    domain = mkOption { default = "karpenoktem.nl"; };
    hostname = mkOption { default = "vipassana.karpenoktem.nl"; };

    ssl.chain = mkOption {
      default = "/etc/letsencrypt/live/sankhara.karpenoktem.nl/chain.pem";
    };

    ssl.cert = mkOption {
      default = "/etc/letsencrypt/live/sankhara.karpenoktem.nl/cert.pem";
    };

    ssl.key = mkOption {
      default = "/etc/letsencrypt/live/sankhara.karpenoktem.nl/privkey.pem";
    };
  };

  config = lib.mkIf cfg.enable {
    services.postfix = {
      enable = true;
      domain = cfg.domain;
      rootAlias = "wortel@${cfg.domain}";
      postmasterAlias = "root";
      extraAliases = ''
        logcheck: root
        devnull: /dev/null
      '';

      #alias_database = hash:/etc/aliases
      hostname = cfg.hostname;
      origin = "$mydomain";
      recipientDelimiter = "+";
      relayDomains = [ "lists.karpenoktem.nl" ];
      destination = [ "$myhostname" "localhost" "local.${cfg.domain}" ];

      sslCert = cfg.ssl.cert;
      sslKey = cfg.ssl.key;

      relayDomains = [
        "khandhas.karpenoktem.com"
        "khandhas.karpenoktem.nl"
        "khandhas.kn.cx"
        "lists.karpenoktem.nl"
        "lists.khandhas.karpenoktem.com"
        "lists.khandhas.karpenoktem.nl"
        "lists.khandhas.kn.cx"
      ];

      # main.cf
      config = {
        # appending .domain is the MUA's job
        append_dot_mydomain = false;
        biff = false;
        broken_sasl_auth_clients = true;
        recipient_bcc_maps = "hash:/etc/postfix/recipient_bcc_maps";

        smtp_tls_CAfile = cfg.ssl.chain; # defaults to ca-bundle?
        smtpd_tls_CAfile = cfg.ssl.chain;

        smtpd_banner = "$myhostname ESMTP NO UCE";
        smtpd_helo_required = true;

        smtpd_sender_restrictions = [
          "check_sender_access hash:/etc/postfix/sender_access"
          "reject_unknown_sender_domain"
          "permit_mynetworks"
          "reject_sender_login_mismatch"
        ];

        mydestination = [ "$myhostname" "localhost" "local.karpenoktem.nl" ];

        mynetworks =
          [ "127.0.0.0/8" "[::ffff:127.0.0.0]/104" "[::1]/128" "10.0.0.3" ];

        # opendkim
        smtpd_milters = [ "inet:localhost:11332" "inet:localhost:8891" ];
        non_smtpd_milters = "inet:localhost:8891";

        sender_canonical_maps = "pcre:/etc/postfix/sender_canonical_map";
        smtp_sasl_password_maps = "hash:/etc/postfix/sasl_passwd";

        smtp_tls_session_cache_database =
          "btree:\${data_directory}/smtp_scache";

        smtpd_sender_login_maps =
          "hash:${config.kn.daan.postfixMapDir}/kninfra_slm_maps";

        smtpd_tls_session_cache_database =
          "btree:\${data_directory}/smtpd_scache";
        virtual_alias_domains = "/etc/postfix/virtual/domains";

        virtual_alias_maps = [
          "hash:/etc/postfix/virtual/pre-maps"
          "hash:${config.kn.daan.postfixMapDir}/kninfra_maps"
          "hash:/etc/postfix/virtual/post-maps"
        ];

        disable_vrfy_command = true;
        mailbox_size_limit = 0; # defaults to 51200000
        mailman_destination_recipient_limit = 1;
        message_size_limit = 51200000; # defaults to 10240000
        smtp_sasl_auth_enable = true;
        # defaults to noplaintext,noanonymous
        smtp_sasl_tls_security_options = "noanonymous";
        smtpd_tls_ciphers = "high";
        smtpd_sasl_auth_enable = true;
        smtpd_sasl_authenticated_header = true;
        smtpd_sasl_local_domain = "";
        #cyrus_sasl_config_path = /etc/postfix/sasl
        relay_recipient_maps = [ "hash:/var/lib/mailman/data/virtual-mailman" ];

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

      transport = ''
        lists.${cfg.domain}    mailman:
      '';

      mapFiles.recipient_bcc_maps =
        pkgs.writeText "postfix-recipient-bcc-maps" ''
          voorzitter@${cfg.domain}  secretaris@${cfg.domain}
        '';

      mapFiles.sender_access = pkgs.writeText "postfix-sender_access" ''
        # todo import from root@sankhara
        /etc/postfix/sender_access
      '';

      enableHeaderChecks = true;

      headerChecks = [
        {
          pattern = "/^From: .*<[a-z]{7}@.*.(eu|ua|us)>/";
          action = "REJECT Looks like spam - please contact us if it isn't.";
        }
        {
          pattern = "/^From: .*@interwood.press>/";
          action = "REJECT Don't spam us";
        }
        {
          pattern = "/^From: .*@.*.nextdoor.nl>/";
          action = "REJECT";
        }
      ];
    };

    networking.firewall.allowedTCPPorts = [ 25 587 465 ];

    environment.systemPackages = with pkgs; [ opendkim postfix rspamd ];
  };
}
