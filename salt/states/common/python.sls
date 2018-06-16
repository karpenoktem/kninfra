python packages:
    pkg.installed:
        - pkgs:
            - python3
            - python3-pip
            - python-pip  # saltstack needs python2 pip

# Python 3 packages used in installing
{% for pkg in ['six'] %}
{{ pkg }}:
    pip.installed:
        - bin_env: /usr/bin/pip3
{% endfor %}
