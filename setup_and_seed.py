import os
import sys

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "techtest.settings")
sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)), "..", ".."))
django.setup()

from django.core import management

from techtest.articles.models import Article
from techtest.authors.models import Author
from techtest.regions.models import Region

# Migrate
management.call_command("migrate", no_input=True)
# Seed

Region.objects.all().delete()
Article.objects.all().delete()
Author.objects.all().delete()

author = Author.objects.create(first_name="user1", last_name="foo")
author2 = Author.objects.create(first_name="user2", last_name="bar")
Article.objects.create(
    title="Fake Article", content="Fake Content", author=author
).regions.set(
    [
        Region.objects.create(code="AL", name="Albania"),
        Region.objects.create(code="UK", name="United Kingdom"),
    ]
)
Article.objects.create(title="Fake Article", content="Fake Content", author=author)
Article.objects.create(title="Fake Article", content="Fake Content", author=author)
Article.objects.create(title="Fake Article", content="Fake Content", author=author)
Article.objects.create(
    title="Fake Article", content="Fake Content", author=author2
).regions.set(
    [
        Region.objects.create(code="AU", name="Austria"),
        Region.objects.create(code="US", name="United States of America"),
    ]
)
