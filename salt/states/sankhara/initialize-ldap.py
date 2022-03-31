#!/usr/bin/env python

# Initializes the LDAP database

import subprocess
import sys
import textwrap


def main():
    if not len(sys.argv) == 7:
        sys.stderr.write('[domain] [admin password] [infra password] ' +
                         '[daan password] [freeradius password] ' +
                         '[saslauthd password]\n')
        sys.exit(-1)
    domain = sys.argv[1]
    suffix = 'dc=' + ',dc='.join(domain.split('.'))
    host = domain.split('.')[0]
    admin_pw, infra_pw, daan_pw, freeradius_pw, saslauthd_pw = [
        subprocess.check_output(['slappasswd', '-s', pw]).strip().decode('utf8')
        for pw in sys.argv[2:7]]
    local = '"gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth"'

    def ldif(s, what='ldapmodify'):
        first_line, rest = s.split('\n', 1)
        s = first_line + '\n' + textwrap.dedent(rest)
        s = s.format(suffix=suffix, host=host, admin_pw=admin_pw,
                     daan_pw=daan_pw, freeradius_pw=freeradius_pw,
                     infra_pw=infra_pw, saslauthd_pw=saslauthd_pw,
                     local=local)
        pipe = subprocess.Popen([what, '-Y', 'EXTERNAL', '-H', 'ldapi:///'],
                                stdin=subprocess.PIPE)
        pipe.stdin.write(s.encode("utf8"))
        pipe.stdin.close()
        if not pipe.wait() == 0:
            raise Exception("%s failed" % what)
    ldif("""dn: olcDatabase={{1}}mdb,cn=config
            changetype: modify
            replace: olcSuffix
            olcSuffix: {suffix}""")
    ldif("""dn: olcDatabase={{1}}mdb,cn=config
            changetype: modify
            replace: olcRootDN
            olcRootDN: cn=admin,{suffix}""")
    ldif("""dn: olcDatabase={{1}}mdb,cn=config
            changetype: modify
            replace: olcRootPW
            olcRootPW: {admin_pw}""")
    ldif("""dn: cn=kn,cn=schema,cn=config
            objectClass: olcSchemaConfig
            cn: kn
            olcattributetypes: {{1}}( 1.3.6.1.4.1.7165.2.1.25 NAME
              'sambaNTPassword' DESC 'MD4 hash of the unicode password'
              EQUALITY caseIgnoreIA5Match SYNTAX
              1.3.6.1.4.1.1466.115.121.1.26{{32}} SINGLE-VALUE )
            olcobjectclasses: {{0}}( 1.3.6.1.4.1.7165.2.2.6 NAME
              'knAccount' DESC 'KN account' SUP top
              AUXILIARY MUST ( uid ) MAY ( sambaNTPassword ) )""",
         'ldapadd')
    # this fails with "no such attribute" since there is no auth
    # but maybe actually check this...
    try:
        ldif("""dn: olcDatabase={{1}}mdb,cn=config
                changetype: modify
                delete: olcAccess""")
    except:
        print("warning: olcAccess deletion failed!!")
    ldif("""dn: olcDatabase={{1}}mdb,cn=config
            changetype: modify
            add: olcAccess
            olcAccess: {{0}}to dn.subtree="ou=users,{suffix}"
              attrs=userPassword,shadowLastChange
              by dn="cn=infra,{suffix}" read
              by dn="cn=daan,{suffix}" write
              by dn="cn=admin,{suffix}" write
              by dn.base={local} write
              by anonymous auth
              by * none""")
    ldif("""dn: olcDatabase={{1}}mdb,cn=config
            changetype: modify
            add: olcAccess
            olcAccess: {{1}}to attrs=sambaNTPassword
              by dn="cn=daan,{suffix}" write
              by dn="cn=freeradius,{suffix}" read
              by dn.base={local} write
              by self write
              by * none""")
    ldif("""dn: olcDatabase={{1}}mdb,cn=config
            changetype: modify
            add: olcAccess
            olcAccess: {{2}}to attrs=userPassword,shadowLastChange
              by self write
              by dn.base={local} write
              by dn="cn=saslauthd,{suffix}" auth
              by dn="cn=daan,{suffix}" write
              by anonymous auth
              by dn="cn=admin,{suffix}" write
              by * none""")
    ldif("""dn: olcDatabase={{1}}mdb,cn=config
            changetype: modify
            add: olcAccess
            olcAccess: {{3}}to dn.subtree="ou=users,{suffix}"
              by dn="cn=freeradius,{suffix}" read
              by dn="cn=saslauthd,{suffix}" read
              by dn="cn=infra,{suffix}" read
              by dn="cn=daan,{suffix}" write
              by dn="cn=admin,{suffix}" write
              by dn.base={local} write
              by * none""")
    ldif("""dn: olcDatabase={{1}}mdb,cn=config
            changetype: modify
            add: olcAccess
            olcAccess: {{4}}to *
              by dn.base={local} write
              by * none""")
    ldif("""dn: {suffix}
            dc: {host}
            objectClass: dcObject
            objectClass: top
            objectClass: organization
            o: {host}""",
         'ldapadd')
    ldif("""dn: ou=users,{suffix}
            ou: users
            objectClass: organizationalUnit
            objectClass: top""",
         'ldapadd')
    ldif("""dn: cn=saslauthd,{suffix}
            cn: saslauthd
            objectClass: organizationalRole
            objectClass: top
            objectClass: simpleSecurityObject
            userPassword: {saslauthd_pw}""",
         'ldapadd')
    ldif("""dn: cn=freeradius,{suffix}
            cn: freeradius
            objectClass: organizationalRole
            objectClass: top
            objectClass: simpleSecurityObject
            userPassword: {freeradius_pw}""",
         'ldapadd')
    ldif("""dn: cn=daan,{suffix}
            cn: daan
            objectClass: organizationalRole
            objectClass: top
            objectClass: simpleSecurityObject
            userPassword: {daan_pw}""",
         'ldapadd')
    ldif("""dn: cn=infra,{suffix}
            cn: infra
            objectClass: organizationalRole
            objectClass: top
            objectClass: simpleSecurityObject
            userPassword: {infra_pw}""",
         'ldapadd')
    with open('/root/.ldap-initialized', 'w'):
        pass


if __name__ == '__main__':
    main()
