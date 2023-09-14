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
        super().__init__(location=location, base_url=base_url, **kwargs)

    def get_available_name(self, name, max_length=None):
        overwrite_file(self, name)
        return name
