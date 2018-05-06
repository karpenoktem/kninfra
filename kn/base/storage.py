from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Override the defaults on the constructor


class OurFileSystemStorage(FileSystemStorage):

    def __init__(self):
        super(OurFileSystemStorage, self).__init__(
            settings.STORAGE_ROOT,
            settings.STORAGE_URL)

# vim: et:sta:bs=2:sw=4:
