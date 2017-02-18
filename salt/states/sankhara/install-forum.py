#!/usr/bin/env python3

import binascii
import os
import subprocess
import sys

import mechanicalsoup

if not len(sys.argv) == 3:
    sys.stderr.write("install-forum.py [forum password] [fqdn]\n")
    sys.exit(1)

password, fqdn = sys.argv[1:]

browser = mechanicalsoup.Browser()

print('1. Requesting install.php')
page = browser.get("http://localhost/forum/admin/install.php")

print('     Filling form')

data = {
    'req_db_type': 'mysqli',
    'req_db_host': 'localhost',
    'req_db_name': 'forum',
    'db_username': 'forum',
    'db_password': password,
    'req_email': 'wortel@%s' % fqdn,
    'req_username': 'admin',
    'req_password1': binascii.hexlify(os.urandom(10)),
    'req_base_url': 'https://%s/forum' % fqdn,
}

form = page.soup.select('form')[0]

for key, val in data.items():
    form.find(attrs={'name': key})['value'] = val

print('2. Submitting settings')
page2 = browser.submit(form, page.url)

try:
    form2 = page2.soup.select('form')[0]
except IndexError:
    sys.stderr.write("\n\nSomething went wrong:\n\n")
    sys.stderr.write(page2.text)
    sys.stderr.write("\n")
    sys.exit(2)

print('3. Downloading config.php')
page3 = browser.submit(form2, page2.url)

print('4. Writing config.php')
config_path = '/srv/forum/config.php'
subprocess.check_call(['touch', config_path])
subprocess.check_call(['chown', 'www-data', config_path])
subprocess.check_call(['chmod', 'og-r', config_path])
with open(config_path, 'w') as f:
    f.write(page3.text)

print('   done!')
