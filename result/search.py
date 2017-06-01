from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Search
from django.conf import settings

connections.create_connection(hosts=[settings.ELASTIC_HOST])

class ResultIndex(DocType):
    type = Text()
    name = Text()
    description = Text()
    url = Text()

    
def search(q):
    s = Search().query('match', all=q)
    response = s.execute()
    return response
