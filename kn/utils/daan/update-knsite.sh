#!/bin/sh -e

cd /srv/karpenoktem.nl/htdocs/site/
git checkout -f
git pull
git fetch --tags
utils/install config.release.php

echo "Done"
