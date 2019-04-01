def calculate_md5(file, block_size=2 ** 20):
    """Returns MD% checksum for given file.
    """
    import hashlib

    md5 = hashlib.md5()
    while True:
        data = file.read(block_size)
        if not data:
            break
        md5.update(data)

    return md5.hexdigest()

