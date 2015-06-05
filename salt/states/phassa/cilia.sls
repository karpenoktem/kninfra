cilia packages:
    pkg.installed:
        - pkgs:
            - python-django
            - msgpack-python
            - python-setuptools
            - python-pyparsing
            - python-markdown
            - python-mysqldb
            - python-pip
            - python-smbpasswd
mirte:
    pip.installed
sarah:
    pip.installed
/root/.profile:
    file.managed:
        - source: salt://phassa/root.profile
        - template: jinja
{% if grains['vagrant'] %}
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
"kninfra clone root":
    git.latest:
        - name: https://github.com/karpenoktem/kninfra
        - target: /root/kninfra
        - user: root
    require:
        - pkg: git
{% endif %}
/root/bin:
    file.symlink:
        - target: /root/kninfra/bin
/root/settings.py:
    file.managed:
        - source: salt://phassa/settings.py
        - template: jinja
        - user: root
        - mode: 600
/var/run/infra:
    file.directory:
        - user: root
