from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Search, Nested, Integer, Q, Keyword
from django.conf import settings

connections.create_connection(hosts=[settings.ELASTIC_HOST])


class ResultIndex(DocType):
    type = Text()
    name = Text()
    description = Text()
    url = Text()
    doctor = Nested(properties={'name': Text(), 'pwz': Integer()})
    categories = Keyword()
    uploaded = Date()
    patient = Nested(properties={'name': Text(), 'first_name': Text(),
                                 'last_name': Text(), 'pesel': Text()})

    class Meta:
        index = 'gabinet'


def search(term):
    q = Q('bool', must=[Q('match_phrase', _all=term)])
    s = Search(index='gabinet').query(q)
    response = s.execute()
    if response.hits.total == 0:
        suggestions = Search(index='gabinet').suggest('suggestion', term, term={'field': '_all'}).execute()
        suggestions = [o['text'] for o in suggestions.suggest['suggestion'][0]['options']]
    else:
        suggestions = []
    return response, suggestions
