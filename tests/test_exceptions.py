from articles.engine import ArticleNotFoundError


def test_article_not_found_error():
    exception = ArticleNotFoundError(year=2020, month=5, day=29, page=None)

    assert str(exception) == (
        "Error loading article. year: 2020, month: 5, day: 29, page: none"
    )
