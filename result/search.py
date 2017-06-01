from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date, Search

connections.create_connection()

class ResultIndex(DocType):
    type = Text()
    name = Text()
    description = Text()
    url = Text()

    
def search(q):
    s = Search().query('match', all=q)
    response = s.execute()
    return response
