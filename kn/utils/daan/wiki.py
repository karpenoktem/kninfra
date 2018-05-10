import binascii
import os
import subprocess

import pymysql

from django.conf import settings


def apply_wiki_changes(daan, changes):
    if not changes:
        return
    creds = settings.WIKI_MYSQL_SECRET
    dc = pymysql.connect(
        host=creds[0],
        user=creds[1],
        password=creds[2],
        db=creds[3],
        charset='utf8'
    )
    try:
        for user, realname, email in changes['add']:
            password = binascii.hexlify(os.urandom(12))
            # Create the user with a random password.
            # WARNING: this password will appear in the logs.
            subprocess.call(['sudo', '-u', settings.MEDIAWIKI_USER,
                             'php', 'maintenance/createAndPromote.php',
                             '--custom-groups=leden',
                             '--quiet',
                             user, password],
                            cwd=settings.MEDIAWIKI_PATH)
            # Set the user email, and reset their password.
            subprocess.call(['sudo', '-u', settings.MEDIAWIKI_USER,
                             'php', 'maintenance/resetUserEmail.php',
                             '--user', user.capitalize(),
                             '--email', email],
                            cwd=settings.MEDIAWIKI_PATH)
            # Set the user real name.
            with dc.cursor() as c:
                c.execute('''
                          UPDATE user
                          SET user_real_name=%s
                          WHERE user_name=%s''',
                          (realname, user.capitalize()))
        for user in changes['remove']:
            with dc.cursor() as c:
                c.execute("DELETE FROM `user` WHERE `user_name`=%s",
                          user.capitalize())
        for user in changes['activate']:
            with dc.cursor() as c:
                # Issue #11: .capitalize() is required due to binary-charset
                c.execute("""INSERT INTO `user_groups` (ug_user, ug_group)
                    SELECT user_id, %s FROM `user` WHERE user_name=%s""",
                          ('leden', user.capitalize()))
        for user in changes['deactivate']:
            with dc.cursor() as c:
                # Issue #11: .capitalize() is required due to binary-charset
                c.execute("""DELETE FROM `user_groups` WHERE ug_group=%s AND
                    ug_user = (SELECT user_id FROM `user` WHERE
                    user_name=%s)""", ('leden', user.capitalize()))
        dc.commit()
    finally:
        dc.close()

# vim: et:sta:bs=2:sw=4:
