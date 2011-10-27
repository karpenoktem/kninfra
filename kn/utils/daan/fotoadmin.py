from kn import settings

import subprocess
import os.path
import grp
import pwd
import os
import re

import MySQLdb

def fotoadmin_create_event(daan, date, name, humanName):
        if not re.match('^20\d{2}-\d{2}-\d{2}$', date):
                return {'error': 'Invalid date'}
        if not re.match('^[a-z0-9-]{3,64}$', name):
                return {'error': 'Invalid name'}
        event = date + '-' + name
        path = os.path.join(settings.PHOTOS_DIR, event)
        if os.path.isdir(path):
                return {'error': 'Event already exists'}
        os.mkdir(path, 0775)
        os.chown(path, pwd.getpwnam('fotos').pw_uid,
                       grp.getgrnam('fotos').gr_gid)
        creds = settings.PHOTOS_MYSQL_CREDS
        dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2],
                                db=creds[3])
        c = dc.cursor()
        c.execute("INSERT INTO fa_albums (name, path, humanname, visibility) "+
                  "VALUE (%s, '', %s, 'hidden')", (event, humanName))
        c.execute("COMMIT;")
        c.close()
        dc.close()
        return {'success': True}

def fotoadmin_move_fotos(daan, event, user, directory):
        if not re.match('^20\d{2}-\d{2}-\d{2}-[a-z0-9-]{3,64}$', event):
                return {'error': 'Invalid event'}
        if not re.match('^[a-z0-9]{3,32}$', user):
                return {'error': 'Invalid user'}
        if not re.match('^[^/\\.][^/]*$', directory):
                return {'error': 'Invalid dir'}
        user_path = os.path.join(settings.USER_DIRS, user)
        if not os.path.isdir(user_path):
                return {'error': 'Invalid user'}
        fotos_path = os.path.join(user_path, 'fotos', directory)
        if not os.path.isdir(fotos_path):
                return {'error': 'Invalid fotodir'}
        if not os.path.realpath(fotos_path).startswith(user_path):
                return {'error': 'Security exception'}
        target_path = os.path.join(settings.PHOTOS_DIR, event)
        if not os.path.isdir(target_path):
                return {'error': 'Event does not exist'}
        base_target_path = os.path.join(target_path, user)
        target_path = base_target_path
        i = 1
        while os.path.isdir(target_path):
                i += 1
                target_path = base_target_path + str(i)
        if subprocess.call(['cp', '-r', fotos_path, target_path]) != 0:
                return {'error': 'cp -r failed'}
        if subprocess.call(['chown', '-R', 'fotos:fotos', target_path]) != 0:
                return {'error': 'chown failed'}
        if subprocess.call(['chmod', '-R', '644', target_path]) != 0:
                return {'error': 'chmod failed'}
        if subprocess.call(['find', target_path, '-type', 'd', '-exec',
                        'chmod', '755', '{}', '+']) != 0:
                return {'error': 'chmod (dirs) failed'}
        visibility = 'hidden'
        creds = settings.PHOTOS_MYSQL_CREDS
        dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2],
                                db=creds[3])
        c = dc.cursor()
        c.execute("SELECT visibility FROM fa_albums WHERE name=%s AND path=''",
                        (event,))
        row = c.fetchone()
        if row and row[0] == 'hidden':
                visibility = 'world'
        c.execute("INSERT INTO fa_albums (name, path, visibility) "+
                  "VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE visibility=%s",
                  (os.path.basename(target_path), event, visibility,
                                                                visibility))
        c.execute("COMMIT;")
        c.close()
        dc.close()
        return {'success': True}
