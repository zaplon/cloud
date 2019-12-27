import os

SOAP_DIR = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'soap')
WSDL = os.path.join(SOAP_DIR, 'wsdl', 'ObslugaRecepty.wsdl')
USE_TRANSPORT = True

