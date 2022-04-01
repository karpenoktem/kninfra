#!/usr/bin/env python

# Initializes the LDAP database

import subprocess
import sys
import textwrap


def main():
    if not len(sys.argv) == 5:
        sys.stderr.write('[domain] [infra password] [daan password] ' +
                         '[saslauthd password]\n')
        sys.exit(-1)
    domain = sys.argv[1]
    suffix = 'dc=' + ',dc='.join(domain.split('.'))
    host = domain.split('.')[0]
    infra_pw, daan_pw, saslauthd_pw = [
        subprocess.check_output(['slappasswd', '-s', pw]).strip().decode('utf8')
        for pw in sys.argv[2:5]]
    local = '"gidNumber=0+uidNumber=0,cn=peercred,cn=external,cn=auth"'

    def ldif(s, what='ldapmodify'):
        first_line, rest = s.split('\n', 1)
        s = first_line + '\n' + textwrap.dedent(rest)
        s = s.format(suffix=suffix, host=host, daan_pw=daan_pw, infra_pw=infra_pw, saslauthd_pw=saslauthd_pw, local=local)
        pipe = subprocess.Popen([what, '-Y', 'EXTERNAL', '-H', 'ldapi:///'],
                                stdin=subprocess.PIPE)
        pipe.stdin.write(s.encode("utf8"))
        pipe.stdin.close()
        if not pipe.wait() == 0:
            raise Exception("%s failed" % what)
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
