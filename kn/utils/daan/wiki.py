import hashlib
import logging
import subprocess

import MySQLdb

from django.conf import settings
from kn.base._random import pseudo_randstr


def wiki_setpass(daan, user, password):
    subprocess.call(['php', 'maintenance/changePassword.php',
                '--user', user,
                '--password', password],
        cwd=settings.MEDIAWIKI_PATH)


def apply_wiki_changes(daan, changes):
    if not changes:
        return
    creds = settings.WIKI_MYSQL_SECRET
    dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2],
                db=creds[3])
    for user, realname, email in changes['add']:
        c = dc.cursor()
        q = """INSERT INTO `user` (`user_name`,
                       `user_real_name`,
                       `user_password`,
                       `user_newpassword`,
                       `user_newpass_time`,
                       `user_email`,
                       `user_touched`,
                       `user_token`,
                       `user_email_authenticated`,
                       `user_email_token`,
                       `user_email_token_expires`,
                       `user_registration`,
                       `user_editcount`)
            VALUES (%s,
                %s,
                0x3437303131623637663034643135386635656232333965626361383933656130,
                '',
                NULL,
                %s,
                '20081102154308',
                '0882a253d72376fb8a1b5c579acba82c',
                NULL,
                NULL,
                NULL,
                '20081102154303',
                0);"""
        c.execute(q, (user.capitalize(), realname, email))
        c.execute("COMMIT;")
        c.close()
    for user in changes['remove']:
        c = dc.cursor()
        c.execute("DELETE FROM `user` WHERE `user_name`=%s",
                user.capitalize())
        c.execute("COMMIT;")
        c.close()
    for user in changes['activate']:
        c = dc.cursor()
        # Issue #11: .capitalize() is required due to binary-charset
        c.execute("""INSERT INTO `user_groups` (ug_user, ug_group)
            SELECT user_id, %s FROM `user` WHERE user_name=%s""",
            ('leden', user.capitalize()))
        c.execute("COMMIT;")
        c.close()
    for user in changes['deactivate']:
        c = dc.cursor()
        # Issue #11: .capitalize() is required due to binary-charset
        c.execute("""DELETE FROM `user_groups` WHERE ug_group=%s AND
            ug_user = (SELECT user_id FROM `user` WHERE
            user_name=%s)""", ('leden', user.capitalize()))
        c.execute("COMMIT;")
        c.close()
    dc.close()

# vim: et:sta:bs=2:sw=4:
