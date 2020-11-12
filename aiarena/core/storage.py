import os

from django.core.files.storage import FileSystemStorage
from private_storage.storage.files import PrivateFileSystemStorage


def overwrite_file(storage, name):
    # If the filename already exists, remove it as if it was a true file system
    if storage.exists(name):
        # move the existing file to a backup, replacing any backup already present
        from_name = os.path.join(storage.location, name)
        to_name = os.path.join(storage.location, name + "_backup")
        os.replace(from_name, to_name)


# https://stackoverflow.com/questions/9522759/imagefield-overwrite-image-file-with-same-name
class OverwriteStorage(FileSystemStorage):
    """
    This file storage solves overwrite on upload problem for storage files.
    """

    def get_available_name(self, name, max_length=None):
        overwrite_file(self, name)
        return name


class OverwritePrivateStorage(PrivateFileSystemStorage):
    """
    This file storage solves overwrite on upload problem for private storage files.
    """

    def __init__(self, location=None, base_url=None, **kwargs):
        super(OverwritePrivateStorage, self).__init__(
            location=location,
            base_url=base_url,
            **kwargs
        )

    def get_available_name(self, name, max_length=None):
        overwrite_file(self, name)
        return name


class HardcodedURLFilenamePrivateStorage(PrivateFileSystemStorage):
    """
    Allows for hard-coding the filename in the url of a filefield
    e.g.
    if a file name has a timestamp in it such as "filename_20201212_201212" then the url can
    be hardcoded as "filename" instead to avoid the ugly timestamp showing to users
    """

    def __init__(self, url_filename=None, location=None, base_url=None, **kwargs):
        super().__init__(
            location=location,
            base_url=base_url,
            **kwargs
        )
        self._url_filename = url_filename

    def url(self, name):
        transformed_name = ('/'.join(name.split('/')[:-1]) + '/' + self._url_filename) \
            if self._url_filename is not None else name
        return super().url(transformed_name)
