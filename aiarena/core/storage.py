import os

from private_storage.storage.files import PrivateFileSystemStorage


# https://stackoverflow.com/questions/9522759/imagefield-overwrite-image-file-with-same-name
class OverwritePrivateStorage(PrivateFileSystemStorage):
    def get_available_name(self, name, max_length=None):
        """
        This file storage solves overwrite on upload problem for private storage files.
        """
        # If the filename already exists, remove it as if it was a true file system
        if self.exists(name):
            # move the existing file to a backup, replacing any backup already present
            from_name = os.path.join(self.location, name)
            to = os.path.join(self.location, name + "_backup")
            os.replace(from_name, to)
        return name
