# vim: et:sta:bs=2:sw=4:
import subprocess

def live_update_knsite(self):
        cwd = '/srv/karpenoktem.nl/htdocs/site'
        for act in [['git', 'checkout', '-f'],
                    ['git', 'pull'],
                    ['git', 'fetch', '--tags'],
                    ['utils/install', 'config.release.php']]:
                if subprocess.call(act, cwd=cwd) != 0:
                        return {'error': str(act)+ " failed"}
        return {'success': True}

def live_update_knfotos(self):
        cwd = '/srv/karpenoktem.nl/htdocs/fotos'
        for act in [['git', 'checkout', '-f'],
                    ['git', 'pull']]:
                if subprocess.call(act, cwd=cwd) != 0:
                        return {'error': str(act)+ " failed"}
        return {'success': True}