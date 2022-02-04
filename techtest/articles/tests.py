import json

from django.test import TestCase
from django.urls import reverse

import techtest.factories as f
from techtest.articles.models import Article
from techtest.regions.models import Region


class ArticleListViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("articles-list")
        self.article_1 = f.ArticleFactory()
        self.region_1 = f.RegionFactory()
        self.region_2 = f.RegionFactory()
        self.article_2 = f.ArticleFactory()
        self.article_2.regions.set([self.region_1, self.region_2])

    def test_serializes_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            [
                {
                    "id": self.article_1.id,
                    "title": self.article_1.title,
                    "content": self.article_1.content,
                    "author": {
                        "id": self.article_1.author.id,
                        "first_name": self.article_1.author.first_name,
                        "last_name": self.article_1.author.last_name,
                    },
                    "regions": [],
                },
                {
                    "id": self.article_2.id,
                    "title": self.article_2.title,
                    "content": self.article_2.content,
                    "author": {
                        "id": self.article_2.author.id,
                        "first_name": self.article_2.author.first_name,
                        "last_name": self.article_2.author.last_name,
                    },
                    "regions": [
                        {
                            "id": self.region_1.id,
                            "code": self.region_1.code,
                            "name": self.region_1.name,
                        },
                        {
                            "id": self.region_2.id,
                            "code": self.region_2.code,
                            "name": self.region_2.name,
                        },
                    ],
                },
            ],
        )

    def test_creates_new_article_with_regions(self):
        author = f.AuthorFactory()
        payload = {
            "title": "Fake Article 3",
            "content": "To be or not to be",
            "author_id": author.id,
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"code": "AU", "name": "Austria"},
            ],
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 2)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 3",
                "content": "To be or not to be",
                "author": {
                    "id": author.id,
                    "first_name": author.first_name,
                    "last_name": author.last_name,
                },
                "regions": [
                    {
                        "id": regions.all()[0].id,
                        "code": "US",
                        "name": "United States of America",
                    },
                    {"id": regions.all()[1].id, "code": "AU", "name": "Austria"},
                ],
            },
            response.json(),
        )

    def test_cannot_creates_new_article_without_author(self):
        payload = {
            "title": "Fake Article 3",
            "content": "To be or not to be",
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"code": "AU", "name": "Austria"},
            ],
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("author_id")[0], "Missing data for required field."
        )

    def test_cannot_creates_new_article_with_invalid_author(self):
        payload = {
            "title": "Fake Article 3",
            "author_id": 0,
            "content": "To be or not to be",
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"code": "AU", "name": "Austria"},
            ],
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("author_id")[0], "Invalid author id.")


class ArticleViewTestCase(TestCase):
    def setUp(self):
        self.article = f.ArticleFactory()
        self.region_1 = f.RegionFactory()
        self.region_2 = f.RegionFactory()
        self.article.regions.set([self.region_1, self.region_2])
        self.url = reverse("article", kwargs={"article_id": self.article.id})

    def test_serializes_single_record_with_correct_data_shape_and_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            {
                "id": self.article.id,
                "title": self.article.title,
                "content": self.article.content,
                "author": {
                    "id": self.article.author.id,
                    "first_name": self.article.author.first_name,
                    "last_name": self.article.author.last_name,
                },
                "regions": [
                    {
                        "id": self.region_1.id,
                        "code": self.region_1.code,
                        "name": self.region_1.name,
                    },
                    {
                        "id": self.region_2.id,
                        "code": self.region_2.code,
                        "name": self.region_2.name,
                    },
                ],
            },
        )

    def test_updates_article_and_regions(self):
        # Change regions
        payload = {
            "title": "Fake Article 1 (Modified)",
            "content": "To be or not to be here",
            "author_id": self.article.author.id,
            "regions": [
                {"code": "US", "name": "United States of America"},
                {"id": self.region_2.id},
            ],
        }
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.first()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 2)
        self.assertEqual(Article.objects.count(), 1)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "content": "To be or not to be here",
                "author": {
                    "id": article.author.id,
                    "first_name": article.author.first_name,
                    "last_name": article.author.last_name,
                },
                "regions": [
                    {
                        "id": self.region_2.id,
                        "code": self.region_2.code,
                        "name": self.region_2.name,
                    },
                    {
                        "id": regions.all()[1].id,
                        "code": "US",
                        "name": "United States of America",
                    },
                ],
            },
            response.json(),
        )
        # Remove regions
        payload["regions"] = []
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        article = Article.objects.last()
        regions = Region.objects.filter(articles__id=article.id)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(article)
        self.assertEqual(regions.count(), 0)
        self.assertDictEqual(
            {
                "id": article.id,
                "title": "Fake Article 1 (Modified)",
                "content": "To be or not to be here",
                "author": {
                    "id": article.author.id,
                    "first_name": article.author.first_name,
                    "last_name": article.author.last_name,
                },
                "regions": [],
            },
            response.json(),
        )

    def test_cannot_updates_article_without_author_id(self):
        payload = {
            "title": "Fake Article 1 (Modified)",
            "content": "To be or not to be here",
            "regions": [
                {"id": self.region_2.id},
            ],
        }
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json().get("author_id")[0], "Missing data for required field."
        )

    def test_cannot_updates_article_with_invalid_author_id(self):
        payload = {
            "title": "Fake Article 1 (Modified)",
            "content": "To be or not to be here",
            "author_id": 0,
            "regions": [
                {"id": self.region_2.id},
            ],
        }
        response = self.client.put(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json().get("author_id")[0], "Invalid author id.")

    def test_removes_article(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Article.objects.count(), 0)
