adminutils packages:
    pkg.installed:
        - pkgs:
            - htop
            - iftop
            - iotop
            - ncdu
            - vim
            {% if pillar['python3'] %}
            - ipython3
            {% else %}
            - ipython
            {% endif %}
            - psmisc
            - socat
/etc/vim/vimrc.local:
    file.managed:
        - source: salt://common/vimrc
