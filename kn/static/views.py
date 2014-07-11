from django.conf import settings

import os.path

# initialize the list of slideshow images for home.html
path = os.path.join(settings.MEDIA_ROOT, 'static/slideshow')
slideshow_images = []
for fn in os.listdir(path):
    slideshow_images.append(os.path.join(settings.MEDIA_URL, 'static/slideshow', fn))

# vim: et:sta:bs=2:sw=4:
