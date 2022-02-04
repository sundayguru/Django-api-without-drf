import factory


class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "authors.Author"

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class RegionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "regions.Region"

    code = factory.LazyAttribute(lambda o: "%s" % o.name[:2].upper())
    name = factory.Faker("country")


class ArticleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "articles.Article"

    title = factory.Faker("name")
    content = factory.Faker("text")
    author = factory.SubFactory(AuthorFactory)
