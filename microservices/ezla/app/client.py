import xmltodict
from requests import Session
from requests.auth import HTTPBasicAuth  # or HTTPDigestAuth, or OAuth1, etc.
from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin

from .settings import WEBSERVICE_USER, WEBSERVICE_PASSWORD, WEBSERVICE_WSDL_URL


class EZLAClient(object):

    def __init__(self, *args, **kwargs):
        session = Session()
        session.verify = False
        history = HistoryPlugin()
        session.auth = HTTPBasicAuth(WEBSERVICE_USER, WEBSERVICE_PASSWORD)
        self.client = Client(WEBSERVICE_WSDL_URL, transport=Transport(session=session), plugins=[history])

    @staticmethod
    def _as_dict(xml):
        return xmltodict.parse(xml)

    def get_xml(self):
        oswiadczenie = self.client.service.pobierzOswiadczenie()
        return oswiadczenie

    def logout(self):
        return self.client.service.usunSesje()

    def get_document_id(self):
        return self.client.service.pobierzIdentyfikatorDokumentu()

