from aiarena.settings import ELO_K


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


# ELO Implementation:
# http://satirist.org/ai/starcraft/blog/archives/117-Elo-ratings-are-easy-to-calculate.html
# winIndicator:
# 1.0 = rating1 won
# 0.0 = rating2 won
# 0.5 = draw
def calculate_elo_delta(rating1, rating2, winIndicator):
    return ELO_K * (winIndicator - calculate_elo_expected_win_rate(rating1, rating2))


def calculate_elo_expected_win_rate(rating1, rating2):
    return 1.0 / (1.0 + 10.0 ** ((rating2 - rating1) / 400.0))
