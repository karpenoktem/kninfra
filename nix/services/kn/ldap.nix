{ pkgs, config, lib, ... }:
let
  cfg = config.kn.ldap;
  inherit (cfg) suffix;
  local = ''"gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth"'';
  globals.passwords.ldap = {
    infra = "CHANGE ME";
    daan = "CHANGE ME";
    saslauthd = "CHANGE ME";
  };
in {
  options.kn.ldap = with lib; {
    enable = mkEnableOption "ldap";
    # todo: deduplicate
    suffix = mkOption {
      type = types.str;
      example = "dc=karpenoktem,dc=nl";
    };
    domain = mkOption {
      type = types.str;
      example = "karpenoktem.nl";
    };
  };

  config = lib.mkIf cfg.enable {
    services.openldap = {
      enable = true;
      urlList = [ "ldapi:///" "ldap://localhost" ];
      settings.children = {
        "olcDatabase={0}config" = {
          attrs = {
            objectClass = "olcDatabaseConfig";
            olcDatabase = "{0}config";
            olcAccess = [
              "{0}to * by dn.exact=uidNumber=0+gidNumber=0,cn=peercred,cn=external,cn=auth manage stop by * none stop"
            ];
          };
        };
        "olcDatabase={1}mdb".attrs = {
          objectClass = [ "olcdatabaseconfig" "olcmdbconfig" ];
          olcDatabase = "{1}mdb";
          olcDbDirectory = "/var/db/openldap";
          olcRootDN = "cn=admin,${suffix}";
          olcSuffix = suffix;
          # run slapindex when changing this
          olcDbIndex = [ "objectClass eq" "uid pres,eq" ];
          olcAccess = [
            ''
              to dn.subtree="ou=users,${suffix}"
               attrs=userPassword,shadowLastChange
               by dn="cn=infra,${suffix}" read
               by dn="cn=daan,${suffix}" write
               by dn.base=${local} write
               by anonymous auth
               by * none
            ''
            ''
              to attrs=sambaNTPassword
               by dn="cn=daan,${suffix}" write
               by dn.base=${local} write
               by self write
               by * none
            ''
            ''
              to attrs=userPassword,shadowLastChange
               by self write
               by dn.base=${local} write
               by dn="cn=saslauthd,${suffix}" auth
               by dn="cn=daan,${suffix}" write
               by anonymous auth
               by * none
            ''
            ''
              to dn.subtree="ou=users,${suffix}"
               by dn="cn=saslauthd,${suffix}" read
               by dn="cn=infra,${suffix}" read
               by dn="cn=daan,${suffix}" write
               by dn.base=${local} write
               by * none
            ''
            ''
              to *
               by dn.base=${local} write
               by * none
            ''
          ];
        };
        "cn=schema".includes =
          (map (schema: "${pkgs.openldap}/etc/schema/${schema}.ldif") [
            "core"
            "cosine"
            "inetorgperson"
            "nis"
          ]);
        "cn=schema".children."cn=kn".attrs = {
          objectClass = "olcSchemaConfig";
          cn = "kn";
          olcAttributeTypes = [''
            ( 1.3.6.1.4.1.7165.2.1.25 NAME
             'sambaNTPassword' DESC 'MD4 hash of the unicode password'
             EQUALITY caseIgnoreIA5Match SYNTAX
             1.3.6.1.4.1.1466.115.121.1.26{32} SINGLE-VALUE )
          ''];
          olcObjectClasses = [''
            ( 1.3.6.1.4.1.7165.2.2.6 NAME
             'knAccount' DESC 'KN account' SUP top
             AUXILIARY MUST ( uid ) MAY ( sambaNTPassword ) )
          ''];
        };
      };
    };
    systemd.services.initialize_ldap = {
      wantedBy = [ "multi-user.target" ];
      after = [ "openldap.service" ];
      requires = [ "openldap.service" ];
      description = "Set LDAP passwords";
      path = [ pkgs.openldap ];
      serviceConfig = {
        # todo: string escape, security
        ExecStart = with globals.passwords.ldap;
          "${pkgs.kninfra}/libexec/initialize-ldap.py ${cfg.domain} ${infra} ${daan} ${saslauthd}";
        Type = "oneshot";
        User = "root";
      };
      # only run when ldap-initialized does not exist
      unitConfig.ConditionPathExists = "!/root/.ldap-initialized";
    };
  };
}
