from django import template
import json

from django.utils.safestring import mark_safe

register = template.Library()


# simple filter which transform context variable into json.
# useful when passing variables to javascript
# for example: {{ employee|as_json }} or {{employee|as_json:'id,name'}} when we are interested only in id and name fields
@register.filter(name='as_json')
def as_json(obj, fields=''):
    if len(fields) > 0:
        fields = fields.split(',')
        result = {f.name: getattr(obj, f.name) for f in obj._meta.fields if f.name in fields}
    else:
        result = {f.name: getattr(obj, f.name) for f in obj._meta.fields}
    return mark_safe(json.dumps(result))
