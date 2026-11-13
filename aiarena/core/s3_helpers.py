from storages.utils import clean_name


AWS_S3_STORAGE_CLASSES = ["PrivateS3BotoStorage", "S3Boto3Storage"]


def is_s3_file(file):
    """
    Quick hack: Returns True if the file is stored on S3, False otherwise.
    """
    return file.storage.__class__.__name__ in AWS_S3_STORAGE_CLASSES


def get_s3_file_size_and_etag(file):
    """
    Returns (size_in_bytes, etag) for a file.

    On S3 these are fetched live via head_object -- we deliberately don't store
    them, since keeping a local copy in sync with S3 would be error-prone. For
    non-S3 backends (dev/test) it falls back to the storage-reported size with a
    null etag, so callers work regardless of environment.
    """
    if not file:
        return 0, None
    if not is_s3_file(file):
        return file.size, None
    storage = file.storage
    s3_key = storage._normalize_name(clean_name(file.name))
    response = storage.connection.meta.client.head_object(Bucket=storage.bucket.name, Key=s3_key)
    return response["ContentLength"], response.get("ETag")


def get_file_s3_url_with_content_disposition(file, file_name):
    """
    Returns a URL to a file with a content disposition header set, if we're using the S3 backend.
    """
    if not is_s3_file(file):
        raise RuntimeError("File storage is not S3")
    return file.storage.url(file.name, parameters={"ResponseContentDisposition": f'inline; filename="{file_name}"'})


def get_file_url_s3_hack(file, file_name):
    """
    Returns a URL to a file with a content disposition header set, if we're using the S3 backend.
    This is a quick hack and ideally should be refactored to work regardless of the storage backend.
    """
    if not file:
        return None

    if is_s3_file(file):
        return get_file_s3_url_with_content_disposition(file, file_name)
    else:
        return file.url
