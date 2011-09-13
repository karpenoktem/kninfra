import hashlib
import logging
import MySQLdb

from kn import settings
from kn.base._random import pseudo_randstr

# NOTE see issue #6 -- MediaWiki's caching can cause confusion

def wiki_setpass(daan, user, password):
        creds = settings.WIKI_MYSQL_CREDS
        dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2],
                                db=creds[3])
        user = user.capitalize()
        c = dc.cursor()
        salt = pseudo_randstr(8)
        h = hashlib.md5(password).hexdigest()
        h = hashlib.md5("%s-%s" % (salt, h)).hexdigest()
        h = ':B:%s:%s' % (salt, h)
        c.execute("UPDATE user SET user_password=%s WHERE user_name=%s;",
                        (h, user))
        c.execute("COMMIT;")
        dc.close()

def apply_wiki_changes(daan, changes):
        creds = settings.WIKI_MYSQL_CREDS
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
                                           `user_options`,
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
                                0x717569636b6261723d310a756e6465726c696e653d320a636f6c733d38300a726f77733d32350a7365617263686c696d69743d32300a636f6e746578746c696e65733d350a636f6e7465787463686172733d35300a736b696e3d0a6d6174683d310a7263646179733d370a72636c696d69743d35300a776c6c696d69743d3235300a686967686c6967687462726f6b656e3d310a737475627468726573686f6c643d300a707265766965776f6e746f703d310a6564697473656374696f6e3d310a6564697473656374696f6e6f6e7269676874636c69636b3d300a73686f77746f633d310a73686f77746f6f6c6261723d310a646174653d64656661756c740a696d61676573697a653d320a7468756d6273697a653d320a72656d656d62657270617373776f72643d300a656e6f74696677617463686c69737470616765733d300a656e6f7469667573657274616c6b70616765733d310a656e6f7469666d696e6f7265646974733d300a656e6f74696672657665616c616464723d300a73686f776e756d626572737761746368696e673d310a66616e63797369673d300a65787465726e616c656469746f723d300a65787465726e616c646966663d300a73686f776a756d706c696e6b733d310a6e756d62657268656164696e67733d300a7573656c697665707265766965773d300a77617463686c697374646179733d330a76617269616e743d6e6c0a6c616e67756167653d6e6c0a7365617263684e73303d31,
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
