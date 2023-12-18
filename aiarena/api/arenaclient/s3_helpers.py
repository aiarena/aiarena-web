AWS_S3_STORAGE_CLASSES = ["PrivateS3BotoStorage", "S3Boto3Storage"]


def is_s3_file(file):
    """
    Quick hack: Returns True if the file is stored on S3, False otherwise.
    """
    return file.storage.__class__.__name__ in AWS_S3_STORAGE_CLASSES


def get_file_s3_url_with_content_disposition(file, file_name):
    """
    Returns a URL to a bot file with a content disposition header set, if we're using the S3 backend.
    """
    if not is_s3_file(file):
        raise RuntimeError("File storage is not S3")
    return file.storage.url(file.name, parameters={"ResponseContentDisposition": f'inline; filename="{file_name}"'})
