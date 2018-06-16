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
            with dc.cursor() as c:
                q = """
        INSERT INTO `user` (`user_name`,
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
        VALUES (
            %s,
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
