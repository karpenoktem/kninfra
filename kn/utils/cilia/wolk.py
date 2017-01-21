# Applies changes to owncloud.  Basiclly forwards everything to wolk.php

import json
import os.path
import logging
import subprocess

from django.conf import settings


def wolk_setpass(cilia, user, passwd):
    if not hasattr(settings, 'WOLK_PATH'):
        logging.warning('wolk: no path available, skipping')
        return None
    wolk_script = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'wolk.php')
    proc = subprocess.Popen(['sudo', '-u', settings.WOLK_USER, 'php',
                             wolk_script], cwd=settings.WOLK_PATH,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.stdin.write(json.dumps({
                        'type': 'setpass',
                        'user': user,
                        'passwd': passwd}))
    proc.stdin.write('\n')
    for l in proc.stdout:
        logging.info("wolk.php: %s" % l[:-1])


def apply_wolk_changes(cilia, changes):
    if not changes:
        return
    wolk_script = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'wolk.php')
    proc = subprocess.Popen(['sudo', '-u', settings.WOLK_USER, 'php',
                             wolk_script], cwd=settings.WOLK_PATH,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    proc.stdin.write(json.dumps({
                        'type': 'apply_changes',
                        'changes': changes}))
    proc.stdin.write('\n')
    for l in proc.stdout:
        logging.info("wolk.php: %s" % l[:-1])

# vim: et:sta:bs=2:sw=4:
