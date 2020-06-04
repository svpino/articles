import os
import glob
import calendar
import markdown
import codecs
import re

from datetime import datetime

from articles.rfeed import Feed, Item, Guid


class Article(object):
    def __init__(
        self, filename: str, author: str = None, transform_fn: callable = None
    ):
        self.filename = filename
        self.transform_fn = transform_fn

        index = filename.rindex("/") + 1

        self.article_id = filename[index + 11 : -3]
        self.year = int(filename[index : index + 4])
        self.month = int(filename[index + 4 : index + 6])
        self.day = int(filename[index + 6 : index + 8])
        self.category = filename[index + 9 : index + 10]
        self.date = datetime(self.year, self.month, self.day)
        self.author = author

    def read(self):
        self.html = markdown.markdown(
            text=codecs.open(self.filename, mode="r", encoding="utf-8").read(),
            extensions=["fenced_code", "codehilite"],
            extension_configs={"codehilite": {"linenums": None}},
        )

        self.title = self._title()
        self.html = re.sub("<h1>(.+?)</h1>", "", self.html, count=1)

        if self.transform_fn is not None:
            self.html = self.transform_fn(self.html)

        self.summary = self._summary()

        return self

    def _title(self):
        matches = re.findall("<h1>(.+?)</h1>", self.html)
        return matches[0] if len(matches) > 0 else ""

    def _summary(self):
        summary = re.findall(
            '<p itemprop="description">(.*?)</p>', self.html, re.DOTALL
        )

        if summary is None or len(summary) == 0:
            summary = ""
            paragraphs = re.findall("<p>(.*?)</p>", self.html, re.DOTALL)
            for p in paragraphs:
                if len(p) > 100:
                    summary = p
                    break
                elif len(p) > len(summary):
                    summary = p
        else:
            summary = summary[0]

        summary = re.sub("<.*?>", "", summary).strip()

        return summary


class Articles(object):
    def __init__(self, articles: list, page: int = None, next: int = None):
        self.articles = articles
        self.page = page
        self.next = next


class Engine(object):
    def __init__(
        self, author: str = None, folder="articles", debug=False, transform_fn=None
    ):
        self.author = author
        self.folder = folder
        self.debug = debug
        self.transform_fn = transform_fn

    def get_articles(self, year=None, month=None, category=None, page=None, total=None):
        def past_articles(filename):
            article_date = datetime(
                int(filename[:4]), int(filename[4:6]), int(filename[6:8])
            )

            return article_date <= datetime.now() or self.debug

        files = list(self._files())
        articles = []
        for filename in files:
            article = self._article(filename=filename, author=self.author)

            # Include only articles that were already published (in other
            # words, don't include anything with a future date)
            if article.date > datetime.now() and not self.debug:
                continue

            if year is not None and article.year != year:
                continue

            if month is not None and article.month != month:
                continue

            if category is not None and article.category != category:
                continue

            articles.append(article)

        if page is not None:
            number_of_posts = len(articles)
            total_number_of_pages = int(number_of_posts / total) + (
                1 if number_of_posts % total > 0 else 0
            )

            if page > total_number_of_pages:
                page = total_number_of_pages

            if page < 1:
                page = 1

            start = (page - 1) * total
            articles = articles[start : total * page]
        elif total is not None:
            articles = articles[:total]

        return Articles(
            articles=[article.read() for article in articles],
            page=page,
            next=(
                page + 1 if page is not None and page < total_number_of_pages else page
            ),
        )

    def get_article(
        self, article_id=None, filename=None, year=None, month=None, day=None
    ):
        if filename is None:
            year = year or "????"
            month = month or "??"
            day = day or "??"
            query = f"{year}{str(month).zfill(2)}{str(day).zfill(2)}??-{article_id}.md"
            path = f"{self.folder}/{query}"

            files = glob.glob(path)
            filename = files[0] if len(files) == 1 else None

        return (
            Article(filename=filename, transform_fn=self.transform_fn).read()
            if filename
            else None
        )

    def get_rss_articles(self, url_fn: callable, total: int = 25):
        articles = []
        for article in self.get_articles(total=total).articles:
            url = url_fn(article)
            articles.append(
                Item(
                    title=article.title,
                    link=url,
                    description=article.html,
                    author=article.author,
                    guid=Guid(url),
                    pubDate=datetime(
                        article.year, article.month, article.day, 12, 0, 0,
                    ),
                )
            )

        return articles

    def _article(
        self, filename: str, author: str = None, transform_fn: callable = None
    ):
        return Article(filename=filename, author=author, transform_fn=transform_fn)

    def _files(self):
        query = f"{self.folder}/??????????-*.md"
        files = sorted(glob.glob(query), reverse=True)
        for filename in files:
            yield filename


class ArticleNotFoundError(Exception):
    def __init__(self, year=None, month=None, day=None, page=None):
        self.year = year or "none"
        self.month = month or "none"
        self.day = day or "none"
        self.page = page or "none"

    def __str__(self):
        return (
            f"Error loading article. year: {self.year}, month: {self.month}, "
            f"day: {self.day}, page: {self.page}"
        )
