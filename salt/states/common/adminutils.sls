adminutils packages:
    pkg.installed:
        - pkgs:
            - htop
            - iftop
            - iotop
            - ncdu
            - vim
            - ipython
            - psmisc
/etc/vim/vimrc.local:
    file.managed:
        - source: salt://common/vimrc
