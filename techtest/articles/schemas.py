from functools import partial

from marshmallow import Schema, ValidationError, fields, validate, validates
from marshmallow.decorators import post_load

from techtest.articles.models import Article
from techtest.authors.models import Author
from techtest.authors.schemas import AuthorSchema
from techtest.regions.models import Region
from techtest.regions.schemas import RegionSchema


class ArticleSchema(Schema):
    class Meta(object):
        model = Article

    id = fields.Integer()
    title = fields.String(validate=validate.Length(max=255))
    content = fields.String()
    regions = fields.Method(
        required=False, serialize="get_regions", deserialize="load_regions"
    )
    author = fields.Nested(AuthorSchema, dump_only=True)
    author_id = fields.Integer(required=True, load_only=True)

    @validates("author_id")
    def validate_author_id(self, author_id):
        try:
            self.author = Author.objects.get(id=author_id)
        except Author.DoesNotExist:
            raise ValidationError("Invalid author id.")

    def get_regions(self, article):
        return RegionSchema().dump(article.regions.all(), many=True)

    def load_regions(self, regions):
        return [
            Region.objects.get_or_create(id=region.pop("id", None), defaults=region)[0]
            for region in regions
        ]

    @post_load
    def update_or_create(self, data, *args, **kwargs):
        regions = data.pop("regions", None)
        article, _ = Article.objects.update_or_create(
            id=data.pop("id", None), author=self.author, defaults=data
        )
        if isinstance(regions, list):
            article.regions.set(regions)

        return article
