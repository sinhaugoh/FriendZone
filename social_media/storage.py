from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


class OverwriteFileStorage(FileSystemStorage):
    def get_available_name(self, name, max_length):
        # If the file name is used, remove it (so that the new one can overwrite)
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name
