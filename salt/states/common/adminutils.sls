adminutils packages:
    pkg.installed:
        - pkgs:
            - htop
            - iftop
            - iotop
            - ncdu
            - vim
            - ipython
/etc/vim/vimrc.local:
    file.managed:
        - source: salt://common/vimrc
