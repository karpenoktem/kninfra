# vim: et:sta:bs=2:sw=4:
from common import *

import gdata.calendar.service

def get_cs():
    username, password = read_ssv_file('gaccount.login')
    cs = gdata.calendar.service.CalendarService()
    cs.email = username
    cs.password = password
    cs.source = 'karpenoktem.nl_sync-1'
    cs.ProgrammaticLogin()
    return cs