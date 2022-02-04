from marshmallow import Schema, ValidationError, fields, validate
from marshmallow.decorators import post_load

from techtest.regions.models import Region


class RegionSchema(Schema):
    class Meta(object):
        model = Region

    id = fields.Integer()
    code = fields.String(required=True, validate=validate.Length(equal=2))
    name = fields.String(validate=validate.Length(max=255))

    @post_load
    def update_or_create(self, data, *args, **kwargs):
        region_id = data.pop("id", None)
        if not region_id:
            if Region.objects.filter(code=data.get("code")).exists():
                raise ValidationError("Region code already exists", "code")

        region, _ = Region.objects.update_or_create(id=region_id, defaults=data)
        return region
