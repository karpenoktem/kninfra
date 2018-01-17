kninfra packages:
    pkg.installed:
        - pkgs:
            {% if pillar['python3'] %}
            - python3-django
            - python3-dev
            - python3-msgpack
            - python3-setuptools
            - python3-pyparsing
            - python3-markdown
            - python3-pymongo
            - python3-pil
            - python3-html2text
            - python3-httplib2
            - python3-pyx
            - python3-unidecode

            # python2 packages for hans
            - python-six
            - python-django
            - python-pymongo

            # prerquisites for pyldap
            - libsasl2-dev
            - libldap2-dev
            - libssl-dev
            {% else %}
            - python-django
            - python-dev
            - msgpack-python
            - python-setuptools
            - python-pyparsing
            - python-markdown
            - python-pymongo
            - python-imaging
            - python-html2text
            - python-httplib2
            - python-ldap
            - python-pyx
            - python-unidecode
            - python-six
            {% endif %}
            - gettext
            - imagemagick

# pip packages
{% for pkg in ['mirte', 'sarah', 'uwsgi', 'tarjan', 'reserved', 'pymysql', 'iso8601', 'google-api-python-client', 'zipseeker', 'sdnotify'] %}
{{ pkg }}:
{% if pillar['python3'] %}
    pip.installed:
        - bin_env: /usr/bin/pip3
{% else %}
    pip.installed
{% endif %}
{% endfor %}

{% if pillar['python3'] %}
{% for pkg in ['pyldap'] %}
{{ pkg }}:
    pip.installed:
        - bin_env: /usr/bin/pip3
{% endfor %}

# python2 packages for hans
{% for pkg in ['mirte', 'sarah', 'msgpack-python'] %}
{{ pkg }} python2:
    pip.installed:
        - name: {{ pkg }}
{% endfor %}
{% endif %}

infra:
    group.present:
        - gid: 2000
    user.present:
        - home: /home/infra
        - uid: 2000
        - shell: /bin/bash
        - groups:
            - infra
            - interinfra
            - list
            {% if grains['vagrant'] %}
            - sudo
            - vagrant
            {% endif %}
fotos:
    group.present:
        - system: true
    user.present:
        - home: /var/fotos
        - system: true
        - shell: /bin/bash
        - createhome: false
        - groups:
            - fotos
/home/infra/.profile:
    file.managed:
        - source: salt://sankhara/infra.profile
        - template: jinja
/root/.profile:
    file.managed:
        - source: salt://sankhara/root.profile
        - template: jinja
{% if grains['vagrant'] %}
/home/infra/repo:
    file.symlink:
        - target: /vagrant
/root/kninfra:
    file.symlink:
        - target: /vagrant
/root/py:
    file.directory
/root/py/vagrantSettingsHack:
    file.directory
/root/py/vagrantSettingsHack/__init__.py:
    file.managed
/root/py/vagrantSettingsHack/settings.py:
    file.symlink:
        - target: /root/settings.py
{% else %}
"kninfra clone infra":
    git.latest:
        - name: https://github.com/karpenoktem/kninfra
        - target: /home/infra/repo
        - user: infra
    require:
        - pkg: git
"kninfra clone root":
    git.latest:
        - name: https://github.com/karpenoktem/kninfra
        - target: /root/kninfra
        - user: root
    require:
        - pkg: git
{% endif %}
/home/infra/scm:
    file.directory:
        - user: infra
/home/infra/py:
    file.directory:
        - user: infra
/home/infra/bin:
    file.symlink:
        - target: /home/infra/repo/bin
/root/bin:
    file.symlink:
        - target: /root/kninfra/bin
/root/settings.py:
    file.managed:
        - source: salt://sankhara/settings-daan.py
        - template: jinja
        - user: root
        - mode: 600
/home/infra/settings.py:
    file.managed:
        - source: salt://sankhara/settings.py
        - template: jinja
        - user: infra
        - mode: 600
https://github.com/awesterb/koert:
    git.latest:
        - user: infra
        - target: /home/infra/scm/koert
    require:
        - pkg: git
/home/infra/py/koert:
    file.symlink:
        - target: /home/infra/scm/koert
https://github.com/karpenoktem/regl:
    git.latest:
        - user: infra
        - target: /home/infra/scm/regl
    require:
        - pkg: git
/home/infra/py/regl:
    file.symlink:
        - target: /home/infra/scm/regl
# We cannot set user/group on /vagrant.  Thus also not on /home/infra/repo.
# We circumvent by using a symlink
/home/infra/repo/kn/settings.py:
    file.symlink:
        - target: /home/infra/settings.py
        {% if grains['vagrant'] %}
        - user: vagrant
        - group: vagrant
        {% endif %}
"giedo mysql user":
    mysql_user.present:
        - host: localhost
        - name: giedo
        - password: {{ pillar['secrets']['mysql_giedo'] }}
/home/infra/vpnkeys:
    file.directory:
        - user: infra
        - mode: 700
/var/run/infra:
    file.directory:
        - user: root
        - group: interinfra
        - mode: 770
/home/infra/storage:
    file.directory:
        - user: infra
/home/infra/storage/smoelen:
    file.directory:
        - user: infra
/home/infra/storage/graphs:
    file.directory:
        - user: infra
/var/fotos:
    file.directory:
        - user: fotos
        - group: fotos
{% if grains['vagrant'] %}
/var/fotos/test:
    file.symlink:
        - target: /home/infra/repo/kn/static/media/img
{% endif %}
/var/cache/fotos:
    file.directory:
        - user: infra
        - group: infra
/etc/default/daan:
    file.managed:
        - source: salt://sankhara/daan.default
        - template: jinja
/etc/default/giedo:
    file.managed:
        - source: salt://sankhara/giedo.default
        - template: jinja
/etc/default/hans:
    file.managed:
        - source: salt://sankhara/hans.default
        - template: jinja
/etc/systemd/system/infra-dir.service:
    file.managed:
        - source: salt://sankhara/infra-dir.service
/etc/systemd/system/daan.service:
    file.managed:
        - source: salt://sankhara/daan.service
/etc/systemd/system/cilia-tunnel.service:
    file.managed:
        - source: salt://sankhara/cilia-tunnel.service
/etc/systemd/system/moniek-tunnel.service:
    file.managed:
        - source: salt://sankhara/moniek-tunnel.service
/etc/systemd/system/giedo.service:
    file.managed:
        - source: salt://sankhara/giedo.service
/etc/systemd/system/django.service:
    file.managed:
        - source: salt://sankhara/django.service
/etc/systemd/system/django.socket:
    file.managed:
        - source: salt://sankhara/django.socket
/etc/systemd/system/hans.service:
    file.managed:
        - source: salt://sankhara/hans.service
/etc/nginx/sankhara.d/90-kninfra.conf:
    file.managed:
        - source: salt://sankhara/kninfra.nginx.conf
        - template: jinja
/home/infra/uwsgi.ini:
    file.managed:
        - source: salt://sankhara/uwsgi.ini
giedo:
    service.running
django.socket:
    service.running
{% if grains['vagrant'] %}
# If using vagrant, redirect the login to `vagrant' to the `infra' user.
/home/vagrant/.bash_login:
    file.managed:
        - contents: cd /home/infra && exec sudo su - infra
/etc/sudoers.d/vagrant-infra:
    file.managed:
        - contents: infra ALL=NOPASSWD:ALL
{% endif %}
