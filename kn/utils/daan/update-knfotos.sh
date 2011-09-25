#!/bin/sh -e

cd /srv/karpenoktem.nl/htdocs/fotos/
git checkout -f
git pull

echo "Done"
