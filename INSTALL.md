Documentation is up here:
https://docs.djangoproject.com/en/1.2/

This has been written for Ubuntu 12.04, but should be useful on other OSes too (especially *nix).

# Requirements:
 * python-django
 * msgpack-python
 * python-setuptools (for mirte)
 * python-pyparsing
 * mongodb (the server)
 * mailman
 * koert, repo: https://github.com/awesterb/koert.git. Add the parent directory of koert to `$PYTHONPATH`
 * regl, repo: https://github.com/karpenoktem/regl.git. Same idea as koert.
 * mirte, install with:

```sh
cd ..
git clone https://github.com/bwesterb/mirte.git
cd mirte
sudo python setup.py install
```

# Run the server
```sh
cd kninfra/kn
PYTHONPATH=/path/to/koert/regl/etc python manage.py runserver
```
Go to, for example http://localhost:8000/smoelen/, to see the server running.
