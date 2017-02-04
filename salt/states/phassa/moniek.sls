moniek packages:
    pkg.installed:
        - pkgs:
            {% if pillar['python3'] %}
            - python3-django
            - python3-msgpack
            - python3-setuptools
            - python3-pyparsing
            - python3-markdown
            - python3-pip
            - python-pip  # saltstack (python 2) needs pip
            {% else %}
            - python-django
            - msgpack-python
            - python-setuptools
            - python-pyparsing
            - python-markdown
            - python-pip
            {% endif %}

# pip packages
{% for pkg in ['mirte', 'sarah', 'GitPython'] %}
{{ pkg }}:
{% if pillar['python3'] %}
    pip.installed:
        - bin_env: /usr/bin/pip3
{% else %}
    pip.installed
{% endif %}
{% endfor %}

/var/run/infra:
    file.directory:
        - user: root
        - group: sys-interinfra
        - dir_mode: 770
kn-boekenlezers:
    group.present:
        - home: /groups/boekenlezers
/groups/boekenlezers:
    file.directory:
        - dir_mode: 770
        - group: kn-boekenlezers
        - user: root
{% if grains['vagrant'] %}
/groups/boekenlezers/fin.gnucash:
    file.managed:
        - source: salt://phassa/fin.gnucash
/groups/boekenlezers/fin.yaml:
    file.managed:
        - source: salt://phassa/fin.yaml
Create fin git repository:
    cmd.script:
        - source: salt://phassa/finCreateTestRepo
        - creates: /groups/boekenlezers/fin
{% endif %}
sys-moniek:
    user.present:
        - home: /home/sys-moniek
        - shell: /bin/bash
        - gid: kn-boekenlezers
        - groups:
            - sys-interinfra
/home/sys-moniek/.profile:
    file.managed:
        - source: salt://phassa/moniek.profile
        - template: jinja
/home/sys-moniek/scm:
    file.directory:
        - user: sys-moniek
/home/sys-moniek/py:
    file.directory:
        - user: sys-moniek
https://github.com/awesterb/koert:
    git.latest:
        - user: sys-moniek
        - target: /home/sys-moniek/scm/koert
    require:
        - pkg: git
/home/sys-moniek/py/koert:
    file.symlink:
        - target: /home/sys-moniek/scm/koert
{% if grains['vagrant'] %}
/home/sys-moniek/kninfra:
    file.symlink:
        - target: /vagrant
/home/sys-moniek/py/vagrantSettingsHack:
    file.directory
/home/sys-moniek/py/vagrantSettingsHack/__init__.py:
    file.managed
/home/sys-moniek/py/vagrantSettingsHack/settings.py:
    file.symlink:
        - target: /home/sys-moniek/settings.py
{% else %}
"moniek kninfra clone root":
    git.latest:
        - name: https://github.com/karpenoktem/kninfra
        - target: /home/sys-moniek/kninfra
        - user: sys-moniek
    require:
        - pkg: git
{% endif %}
/home/sys-moniek/bin:
    file.symlink:
        - target: /home/sys-moniek/kninfra/bin
/home/sys-moniek/settings.py:
    file.managed:
        - source: salt://phassa/settings.py
        - template: jinja
        - user: sys-moniek
        - mode: 600
/etc/default/moniek:
    file.managed:
        - source: salt://phassa/moniek.default
        - template: jinja
/etc/systemd/system/moniek.service:
    file.managed:
        - source: salt://phassa/moniek.service
moniek:
    service.running
