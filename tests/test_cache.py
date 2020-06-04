import time

from articles.cache import cache


def test_cache():
    count = 0

    @cache(seconds=1)
    def test(arg1):
        nonlocal count
        count += 1
        return count

    assert test(1) == 1, "Function should be called the first time we invoke it"
    assert test(1) == 1, "Function should not be called because it is already cached"

    # Let's now wait for the cache to expire
    time.sleep(1)

    assert test(1) == 2, "Function should be called because the cache already expired"
