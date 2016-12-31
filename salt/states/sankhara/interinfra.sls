# We have to create this group before we install nginx. Otherwise the reloaded
# running nginx process won't have access to the Django socket.
interinfra:
    group.present:
        - gid: 3000
        - addusers:
            - www-data
