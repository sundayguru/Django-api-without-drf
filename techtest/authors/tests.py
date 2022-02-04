import json

from django.test import TestCase
from django.urls import reverse

import techtest.factories as f
from techtest.authors.models import Author
from techtest.regions.models import Region


class AuthorListTestCase(TestCase):
    def setUp(self):
        self.url = reverse("authors-list")
        f.AuthorFactory.create_batch(size=3)

    def test_api_user_can_list_authors(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

    def test_object_keys(self):
        expected = {"id", "first_name", "last_name"}
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(expected, set(response.json()[0].keys()))


class AuthorCreateTestCase(TestCase):
    def setUp(self):
        self.url = reverse("authors-list")

    def test_api_user_can_creates_new_author(self):
        payload = {
            "first_name": "user1",
            "last_name": "foo",
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)

        author = Author.objects.last()
        self.assertIsNotNone(author)
        self.assertDictEqual(
            {"id": author.id, **payload},
            response.json(),
        )

    def test_api_user_cannot_creates_without_first_name(self):
        payload = {
            "last_name": "foo",
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json().get("first_name"))

    def test_api_user_cannot_creates_without_last_name(self):
        payload = {
            "first_name": "user",
        }
        response = self.client.post(
            self.url, data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json().get("last_name"))


class AuthorRetrieveTestCase(TestCase):
    def test_api_user_can_retrieve_author(self):
        author = f.AuthorFactory(first_name="test", last_name="user")
        response = self.client.get(reverse("author", kwargs={"author_id": author.id}))
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            response.json(),
            {
                "id": author.id,
                "first_name": "test",
                "last_name": "user",
            },
        )

    def test_api_user_cannot_retrieve_author_with_invalid_id(self):
        response = self.client.get(reverse("author", kwargs={"author_id": 10}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json().get("error"), "No Author matches the given query"
        )


class AuthorUpdateTestCase(TestCase):
    def test_user_can_updates_author(self):
        author = f.AuthorFactory()
        payload = {
            "id": author.id,
            "first_name": "user",
            "last_name": "bar",
        }
        response = self.client.put(
            reverse("author", kwargs={"author_id": author.id}),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        author.refresh_from_db()
        self.assertEqual(author.first_name, "user")
        self.assertEqual(author.last_name, "bar")
        self.assertDictEqual(
            {
                "id": author.id,
                "first_name": "user",
                "last_name": "bar",
            },
            response.json(),
        )

    def test_user_cannot_updates_author_without_required_fields(self):
        author = f.AuthorFactory()
        payload = {
            "id": author.id,
        }
        response = self.client.put(
            reverse("author", kwargs={"author_id": author.id}),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        assert "first_name" in response_data
        assert "last_name" in response_data


class AuthorDeleteTestCase(TestCase):
    def test_user_can_delete_author(self):
        author = f.AuthorFactory()
        response = self.client.delete(
            reverse("author", kwargs={"author_id": author.id})
        )
        self.assertEqual(response.status_code, 204)
        assert not Author.objects.all().exists()

    def test_user_cannot_delete_author_with_invalid_id(self):
        response = self.client.delete(reverse("author", kwargs={"author_id": 3}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json().get("error"), "No Author matches the given query"
        )
