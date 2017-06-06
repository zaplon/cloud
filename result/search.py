from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Search, Nested, Integer, Q
from django.conf import settings

connections.create_connection(hosts=[settings.ELASTIC_HOST])


class ResultIndex(DocType):
    type = Text()
    name = Text()
    description = Text()
    url = Text()
    doctor = Nested(properties={'name': Text(), 'pwz': Integer()})
    uploaded = Date()
    patient = Nested(properties={'first_name': Text(), 'last_name': Text(), 'pesel': Text()})

    class Meta:
        index = 'gabinet'


def search(term):
    q = Q('bool', should=[Q('match', _all=term)])
    s = Search(index='gabinet').query(q)
    response = s.execute()
    if response.hits.total < 5:
        suggestions = Search(index='gabinet').suggest('suggestion', term, term={'field': '_all'}).execute_suggest()
        suggestions = [o.text for o in suggestions['suggestion'][0]['options']]
    else:
        suggestions = []
    return response, suggestions
