import os

SOAP_DIR = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'soap')
# PRIVATE_KEY = os.path.join(SOAP_DIR, 'keys', 'Adam158 Leczniczy.p12')
PRIVATE_KEY = os.path.join(SOAP_DIR, 'keys', 'key.pem')
PUBLIC_KEY = os.path.join(SOAP_DIR, 'keys', 'Podmiot_leczniczy_158-WSS.cer')
# CLIENT_CERT = os.path.join(SOAP_DIR, 'keys', 'client_cert.pem')

CLIENT_P12 = os.path.join(SOAP_DIR, 'keys', 'Podmiot_leczniczy_158-TLS.p12')
CLIENT_P12_PASS = 'VfkxFEnqyt'

WSSE_P12 = os.path.join(SOAP_DIR, 'keys', 'Podmiot_leczniczy_158-WSS.p12')
WSSE_P12_PASS = 'VfkxFEnqyt'

PRESCRIPTION_P12 = os.path.join(SOAP_DIR, 'keys', 'Adam158 Leczniczy.p12')
PRESCRIPTION_P12_PASS = 'VfkxFEnqyt'

#CLIENT_P12 = os.path.join(SOAP_DIR, 'keys', 'Praktyka_lekarska_39-tls.p12')
#CLIENT_P12_PASS = '8Y8aP3CSxf'

KEY_PASSWORD = '8Y8aP3CSxf'

idPodmiotuOidRoot = '2.16.840.1.113883.3.4424.2.3.1'
idPodmiotuOidExt = '000000926670'
idPodmiotuLokalne = '2.16.840.1.113883.3.4424.2.7.293'
idPracownikaOidRoot = '2.16.840.1.113883.3.4424.1.6.2'
idPracownikaOidExt = '5992363'
idMiejscaPracyOidRoot = '2.16.840.1.113883.3.4424.2.3.2'
idMiejscaPracyOidExt = '4'
rolaBiznesowa = 'LEKARZ_LEK_DENTYSTA_FELCZER'

WSDL = os.path.join(SOAP_DIR, 'wsdl_prod', 'ObslugaRecepty.wsdl')
USE_TRANSPORT = False

if os.environ.get('P1_ENV') == 'dev':
    local_settings = os.path.join(os.path.dirname(__file__), 'dev_settings.py')
    if os.path.isfile(local_settings):
        from .dev_settings import *

