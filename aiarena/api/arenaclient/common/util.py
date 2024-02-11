from aiarena.core.s3_helpers import is_s3_file


def obtain_s3_filehash_or_default(file, default):
    """
    Returns the ETAG of the file if it's stored on S3, otherwise returns the default value provided.
    """
    assert file is not None, "file is None"

    # if the file is stored on S3, then return it's ETAG
    if is_s3_file(file):
        path_prefix = file.storage.location
        hash = file.storage.bucket.Object(path_prefix + file.name).e_tag
        return remove_quotes(hash)
    else:
        return default


def remove_quotes(etag):
    # [1:-1] is to remove the quotes from the ETAG
    return etag[1:-1]
