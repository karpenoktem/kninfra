#!/usr/bin/env python

# Initializes the LDAP database

import sys
import subprocess

def ldif(s, what='ldapmodify'):
    s = '\n'.join([l.strip() for l in s.split('\n')])
    pipe = subprocess.Popen([what, '-Y', 'EXTERNAL', '-H', 'ldapi:///'],
                            stdin=subprocess.PIPE)
    pipe.stdin.write(s)
    pipe.stdin.close()
    if not pipe.wait() == 0:
        raise Exception("%s failed" % what)

def main():
    if not len(sys.argv) == 6:
        sys.stderr.write('[domain] [admin password] [infra password] '+
                                '[daan password] [freeradius password]\n')
        sys.exit(-1)
    domain = sys.argv[1]
    suffix = 'dc='+ ',dc='.join(domain.split('.'))
    host = domain.split('.')[0]
    admin_pw, infra_pw, daan_pw, freeradius_pw = [
                subprocess.check_output(['slappasswd', '-s', pw]).strip()
                        for pw in sys.argv[2:6]]
    ldif("""dn: olcDatabase={1}mdb,cn=config
            changetype: modify
            replace: olcSuffix
            olcSuffix: %s""" % suffix)
    ldif("""dn: olcDatabase={1}mdb,cn=config
            changetype: modify
            replace: olcRootDN
            olcRootDN: cn=admin,%s""" % suffix)
    ldif("""dn: olcDatabase={1}mdb,cn=config
            changetype: modify
            replace: olcRootPW
            olcRootPW: %s""" % admin_pw)
    ldif("""dn: cn=kn,cn=schema,cn=config
            objectClass: olcSchemaConfig
            cn: kn\n"""+
            "olcattributetypes: {1}( 1.3.6.1.4.1.7165.2.1.25 NAME "+
            "'sambaNTPassword' DESC 'MD4 hash of the unicode password' "+
            "EQUALITY caseIgnoreIA5Match SYNTAX 1.3.6.1.4.1.1466.115.12"+
            "1.1.26{32} SINGLE-VALUE )\n"+
            " olcobjectclasses: {0}( 1.3.6.1.4"+
            ".1.7165.2.2.6 NAME 'knAccount' DESC 'KN account' SUP top "+
            "AUXILIARY MUST ( uid ) MAY ( sambaNTPassword ) )\n",
                'ldapadd')
    ldif("""dn: olcDatabase={1}mdb,cn=config
            changetype: modify
            delete: olcAccess""")
    ldif("""dn: olcDatabase={1}mdb,cn=config
            changetype: modify
            add: olcAccess\n"""+
            'olcAccess: {0}to *'+
            ' by dn.base="gidNumber=0+uidNumber=0,cn=peercred,cn=external,'+
                    'cn=auth" write'+
            ' by * none')
    ldif(("""dn: olcDatabase={1}mdb,cn=config
            changetype: modify
            add: olcAccess\n"""+
            'olcAccess: {1}to dn.subtree="ou=users,%s"'+
            ' attrs=userPassword,shadowLastChange'+
            ' by dn="cn=infra,%s" read'+
            ' by dn="cn=daan,%s" write'+
            ' by dn="cn=admin,%s" write'+
            ' by anonymous auth'+
            ' by * none') % (suffix, suffix, suffix, suffix))
    ldif(("""dn: olcDatabase={1}mdb,cn=config
            changetype: modify
            add: olcAccess\n"""+
            'olcAccess: {2}to attrs=sambaNTPassword'+
            ' by dn="cn=daan,%s" write'+
            ' by dn="cn=freeradius,%s" read'+
            ' by self write'+
            ' by * none') % (suffix, suffix))
    ldif(("""dn: olcDatabase={1}mdb,cn=config
            changetype: modify
            add: olcAccess\n"""+
            'olcAccess: {3}to attrs=userPassword,shadowLastChange'+
            ' by self write'+
            ' by anonymous auth'+
            ' by dn="cn=admin,%s" write'+
            ' by * none') % (suffix,))
    ldif(("""dn: olcDatabase={1}mdb,cn=config
            changetype: modify
            add: olcAccess\n"""+
            'olcAccess: {1}to dn.subtree="ou=users,%s"'+
            ' by dn="cn=freeradius,%s" read'+
            ' by dn="cn=infra,%s" read'+
            ' by dn="cn=daan,%s" write'+
            ' by dn="cn=admin,%s" write'+
            ' by * none') % (suffix, suffix, suffix, suffix, suffix))
    ldif("""dn: %s
            dc: %s
            objectClass: dcObject
            objectClass: top
            objectClass: organization
            o: %s""" % (suffix, host, host),
                'ldapadd')
    ldif("""dn: cn=freeradius,%s
            cn: freeradius
            objectClass: organizationalRole
            objectClass: top
            objectClass: simpleSecurityObject
            userPassword: %s""" % (suffix, freeradius_pw),
                'ldapadd')
    ldif("""dn: cn=daan,%s
            cn: daan
            objectClass: organizationalRole
            objectClass: top
            objectClass: simpleSecurityObject
            userPassword: %s""" % (suffix, daan_pw),
                'ldapadd')
    ldif("""dn: cn=infra,%s
            cn: infra
            objectClass: organizationalRole
            objectClass: top
            objectClass: simpleSecurityObject
            userPassword: %s""" % (suffix, infra_pw),
                'ldapadd')
    with open('/root/.ldap-initialized', 'w') as f:
        pass

if __name__ == '__main__':
    main()
