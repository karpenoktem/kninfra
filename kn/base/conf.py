from django.conf import settings

def from_settings_import(*args):
    """     from_settings_import('SOME_VARIABLE', 'DT_MIN', globals())
    
        does what you would expect the following to do
    
            from django.conf.settings import SOME_VARIABLE, DT_MIN """
    for name in args[:-1]:
        args[-1][name] = getattr(settings, name)

# vim: et:sta:bs=2:sw=4:
