import hashlib


"""
This serves as a reference implement for the S3 etag calculation.
It takes into account the format of multipart uploads, and the fact that the etag is a hash of the concatenated md5s of 
the parts, followed by a dash and the number of parts.
This has been confirmed to work on at least one large multipart upload bot file (it was ~250 MB), 
as well as a non-multipart upload map file (4.4 MB).
"""


def calculate_s3_etag(file_path, chunk_size=8 * 1024 * 1024):
    md5s = []

    with open(file_path, "rb") as fp:
        while True:
            data = fp.read(chunk_size)
            if not data:
                break
            md5s.append(hashlib.md5(data))

    if len(md5s) < 1:
        return hashlib.md5().hexdigest()

    if len(md5s) == 1:
        return md5s[0].hexdigest()

    digests = b"".join(m.digest() for m in md5s)
    digests_md5 = hashlib.md5(digests)
    return f'"{digests_md5.hexdigest()}-{len(md5s)}"'


md5 = calculate_s3_etag("/home/lladdy/Downloads/RomanticideAIE")
print(md5)
