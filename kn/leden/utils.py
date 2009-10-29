from subprocess import Popen, PIPE
from kn import settings

class ChangePasswordError(Exception):
	pass

def change_password(username, oldpassword, newpassword):
	pipe = Popen([settings.SMOELEN_CHPASSWD_PATH, username], 
			stdin=PIPE, stdout=PIPE, stderr=PIPE)
	try:
		out, err = pipe.communicate("%s\n%s\n"
				% (oldpassword,newpassword))	
	except Exception as e:
		raise ChangePasswordError("te maken met een interne fout"
				"en wel met het openen van exec_autsetpass")
	
	if pipe.returncode==256-1:
		raise ChangePasswordError("geen fatsoenlijk nieuw wachtwoord"
				" ingevoerd (alleen spaties e.d.?)")
	if pipe.returncode==256-2:
		raise ChangePasswordError("geen fatsoenlijk nieuw wachtwoord"
				" ingevoerd")
	if pipe.returncode==256-3:
		raise ChangePasswordError(" geen fatsoenlijke (?!)"
				" gebruikersnaam")
	if pipe.returncode==10:
		raise ChangePasswordError("niet het oude wachtwoord ingevuld")
	if pipe.returncode!=0:
		raise ChangePasswordError("te maken met een onverwachte"
				" interne fout, code %s" % pipe.returncode)
