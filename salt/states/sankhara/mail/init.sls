mail packages:
    pkg.installed:
        - pkgs:
            - postfix-pcre
            - libsasl2-modules
            - sasl2-bin
postfix:
    service:
        - running
saslauthd:
    service:
        - running
/etc/postfix/main.cf:
    file.managed:
        - source: salt://sankhara/mail/main.cf
        - template: jinja
        - watch_in:
            - service: postfix
/etc/postfix/virtual:
    file.directory
/etc/postfix/sasl:
    file.directory
/etc/postfix/sasl/smtpd.conf:
    file.managed:
        - source: salt://sankhara/mail/sasl/smtpd.conf
        - template: jinja
        - watch_in:
            - service: postfix
        - require:
            - file: /etc/postfix/sasl
/etc/postfix/sender_canonical_map:
    file.managed:
        - source: salt://sankhara/mail/sender_canonical_map
        - template: jinja
        - watch_in:
            - service: postfix
{% for file in ['transport', 'sender_access',
                'virtual/domains', 'virtual/pre-maps', 'virtual/post-maps'] %}
/etc/postfix/{{ file }}:
    file.managed:
        - source: salt://sankhara/mail/{{ file }}
        - template: jinja
    cmd.wait:
        - name: postmap /etc/postfix/{{ file }}
        - watch:
            - file: /etc/postfix/{{ file }}
        - watch_in:
            - service: postfix
        - require:
            - file: /etc/postfix/virtual
            - pkg: mail packages
{% endfor %}
/etc/default/saslauthd:
    file.managed:
        - source: salt://sankhara/mail/saslauthd.default
        - watch_in:
            - service: saslauthd
/etc/saslauthd.conf:
    file.managed:
        - source: salt://sankhara/mail/saslauthd.conf
        - template: jinja
        - watch_in:
            - service: saslauthd
