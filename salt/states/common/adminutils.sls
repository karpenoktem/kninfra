htop:
    pkg:
        - installed
iftop:
    pkg:
        - installed
iotop:
    pkg:
        - installed
ncdu:
    pkg:
        - installed
vim:
    pkg:
        - installed
/etc/vim/vimrc.local:
    file.managed:
        - source: salt://common/vimrc
