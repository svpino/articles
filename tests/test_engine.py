import os
import pytest

from articles.engine import Engine, Article, Articles


class MockArticle(Article):
    def __init__(self, filename):
        super().__init__(filename)

    def read(self):
        return self


@pytest.fixture(scope="function")
def engine():
    engine = Engine()
    return engine


def test_get_articles_doesnt_include_future_articles(engine, monkeypatch):
    monkeypatch.setattr(
        engine,
        "_files",
        lambda: [
            "folder/2080031800-file1.md",
            "folder/2020031800-file2.md",
            "folder/2020031800-file3.md",
        ],
    )
    monkeypatch.setattr(
        engine,
        "_article",
        lambda **kwargs: MockArticle(filename=kwargs.pop("filename", None)),
    )

    engine.debug = False
    articles = engine.get_articles(total=10)

    assert len(articles.articles) == 2
    assert articles.articles[0].filename == "folder/2020031800-file2.md"
    assert articles.articles[1].filename == "folder/2020031800-file3.md"

    engine.debug = True
    articles = engine.get_articles(total=10)

    assert len(articles.articles) == 3


def test_get_articles_filters_by_year(engine, monkeypatch):
    monkeypatch.setattr(
        engine,
        "_files",
        lambda: [
            "folder/2020031800-file1.md",
            "folder/2020031800-file2.md",
            "folder/2021031800-file3.md",
        ],
    )
    monkeypatch.setattr(
        engine,
        "_article",
        lambda **kwargs: MockArticle(filename=kwargs.pop("filename", None)),
    )

    engine.debug = True

    articles = engine.get_articles(total=10, year=2020)
    assert len(articles.articles) == 2
    assert articles.articles[0].filename == "folder/2020031800-file1.md"
    assert articles.articles[1].filename == "folder/2020031800-file2.md"

    articles = engine.get_articles(total=10, year=2021)
    assert len(articles.articles) == 1
    assert articles.articles[0].filename == "folder/2021031800-file3.md"


def test_get_articles_filters_by_month(engine, monkeypatch):
    monkeypatch.setattr(
        engine,
        "_files",
        lambda: [
            "folder/2020031800-file1.md",
            "folder/2020031800-file2.md",
            "folder/2020041800-file3.md",
        ],
    )
    monkeypatch.setattr(
        engine,
        "_article",
        lambda **kwargs: MockArticle(filename=kwargs.pop("filename", None)),
    )

    engine.debug = True

    articles = engine.get_articles(total=10, month=3)
    assert len(articles.articles) == 2
    assert articles.articles[0].filename == "folder/2020031800-file1.md"
    assert articles.articles[1].filename == "folder/2020031800-file2.md"

    articles = engine.get_articles(total=10, month=4)
    assert len(articles.articles) == 1
    assert articles.articles[0].filename == "folder/2020041800-file3.md"


def test_get_articles_filters_by_category(engine, monkeypatch):
    monkeypatch.setattr(
        engine,
        "_files",
        lambda: [
            "folder/202003180a-file1.md",
            "folder/202003180a-file2.md",
            "folder/202003180b-file3.md",
        ],
    )
    monkeypatch.setattr(
        engine,
        "_article",
        lambda **kwargs: MockArticle(filename=kwargs.pop("filename", None)),
    )

    engine.debug = True

    articles = engine.get_articles(total=10, category="a")
    assert len(articles.articles) == 2
    assert articles.articles[0].filename == "folder/202003180a-file1.md"
    assert articles.articles[1].filename == "folder/202003180a-file2.md"

    articles = engine.get_articles(total=10, category="b")
    assert len(articles.articles) == 1
    assert articles.articles[0].filename == "folder/202003180b-file3.md"


def test_get_articles_pagination(engine, monkeypatch):
    monkeypatch.setattr(
        engine,
        "_files",
        lambda: [
            "folder/202003180a-file1.md",
            "folder/202003180a-file2.md",
            "folder/202003180b-file3.md",
            "folder/202003180b-file3.md",
            "folder/202003180b-file3.md",
            "folder/202003180b-file3.md",
            "folder/202003180b-file3.md",
            "folder/202003180b-file3.md",
            "folder/202003180b-file3.md",
            "folder/202003180b-file3.md",
        ],
    )
    monkeypatch.setattr(
        engine,
        "_article",
        lambda **kwargs: MockArticle(filename=kwargs.pop("filename", None)),
    )

    engine.debug = True

    assert len(engine.get_articles(page=1, total=3).articles) == 3
    assert len(engine.get_articles(page=2, total=3).articles) == 3
    assert len(engine.get_articles(page=3, total=3).articles) == 3
    assert len(engine.get_articles(page=4, total=3).articles) == 1