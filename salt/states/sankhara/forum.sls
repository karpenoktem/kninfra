forum mysql:
    mysql_user.present:
        - host: localhost
        - name: forum
        - password: {{ pillar['secrets']['mysql_forum'] }}
    mysql_database.present:
        - name: forum
forum mysql grant 1:
    mysql_grants.present:
        - grant: all privileges
        - database: forum.*
        - user: forum
# forum mysql grant 2:
#     mysql_grants.present:
#         - grant: select
#         - database: forum.users
#         - user: giedo
