from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import DocType, Text, Date

connections.create_connection()

class ResultIndex(DocType):
    type = Text()
    name = Text()
    description = Text()
    url = Text()
