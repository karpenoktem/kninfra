mail packages:
    pkg.installed:
        - pkgs:
            - postfix
postfix:
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
{% for file in ['transport', 'sender_access', 'sender_canonical_map',
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
