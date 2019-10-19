import os
from OpenSSL import crypto
from zeep.wsse.signature import BinarySignature
from lxml import etree
from lxml.etree import QName

from zeep import ns
from zeep.utils import detect_soap_env
from zeep.wsse.utils import get_security_header, ensure_id
from zeep.wsse.signature import _sign_node, _make_sign_key

try:
    import xmlsec
except ImportError:
    xmlsec = None


class Signature(BinarySignature):
    def verify(self, envelope):
        return envelope

    def apply(self, envelope, headers):
        key = _make_sign_key(self.key_data, self.cert_data, self.password)
        _sign_envelope_with_key_binary(
            envelope, key, self.signature_method, self.digest_method
        )
        return envelope, headers


def _sign_envelope_with_key_binary(envelope, key, signature_method, digest_method):
    security, sec_token_ref, x509_data = _signature_prepare(
        envelope, key, signature_method, digest_method
    )
    ref = etree.SubElement(
        sec_token_ref,
        QName(ns.WSSE, "Reference"),
        {
            "ValueType": "http://docs.oasis-open.org/wss/2004/01/"
            "oasis-200401-wss-x509-token-profile-1.0#X509v3"
        },
    )
    bintok = etree.Element(
        QName(ns.WSSE, "BinarySecurityToken"),
        {
            "ValueType": "http://docs.oasis-open.org/wss/2004/01/"
            "oasis-200401-wss-x509-token-profile-1.0#X509v3",
            "EncodingType": "http://docs.oasis-open.org/wss/2004/01/"
            "oasis-200401-wss-soap-message-security-1.0#Base64Binary",
        },
    )
    ref.attrib["URI"] = "#" + ensure_id(bintok)
    bintok.text = x509_data.find(QName(ns.DS, "X509Certificate")).text
    security.insert(1, bintok)
    x509_data.getparent().remove(x509_data)


def _signature_prepare(envelope, key, signature_method, digest_method):
    """Prepare envelope and sign."""
    soap_env = detect_soap_env(envelope)

    # Create the Signature node.
    signature = xmlsec.template.create(
        envelope,
        xmlsec.Transform.EXCL_C14N,
        signature_method or xmlsec.Transform.RSA_SHA1,
    )

    # Add a KeyInfo node with X509Data child to the Signature. XMLSec will fill
    # in this template with the actual certificate details when it signs.
    key_info = xmlsec.template.ensure_key_info(signature)
    x509_data = xmlsec.template.add_x509_data(key_info)
    xmlsec.template.x509_data_add_issuer_serial(x509_data)
    xmlsec.template.x509_data_add_certificate(x509_data)

    # Insert the Signature node in the wsse:Security header.
    security = get_security_header(envelope)
    security.insert(0, signature)

    # Perform the actual signing.
    ctx = xmlsec.SignatureContext()
    ctx.key = key
    _sign_node(ctx, signature, envelope.find(QName(soap_env, "Body")), digest_method)
    kontekst_wywolania = envelope.getchildren()[0].getchildren()[0]
    _sign_node(ctx, signature, kontekst_wywolania, digest_method)
    timestamp = security.find(QName(ns.WSU, "Timestamp"))
    if timestamp != None:
        _sign_node(ctx, signature, timestamp)
    ctx.sign(signature)

    # Place the X509 data inside a WSSE SecurityTokenReference within
    # KeyInfo. The recipient expects this structure, but we can't rearrange
    # like this until after signing, because otherwise xmlsec won't populate
    # the X509 data (because it doesn't understand WSSE).
    sec_token_ref = etree.SubElement(key_info, QName(ns.WSSE, "SecurityTokenReference"))
    return security, sec_token_ref, x509_data


class PKCS12Manager():

    def __init__(self, p12file, passphrase):
        self.p12file = p12file
        self.unlock = passphrase
        self.webservices_dir = ''
        self.keyfile = ''
        self.certfile = ''

        # Get filename without extension
        ext = os.path.splitext(p12file)
        self.filebasename = os.path.basename(ext[0])

        self.createPrivateCertStore()
        self.p12topem()

    def getKey(self):
        return self.keyfile

    def getCert(self):
        return self.certfile

    def createPrivateCertStore(self):
        home = os.path.expanduser('~')
        webservices_dir = os.path.join(home, '.webservices')
        if not os.path.exists(webservices_dir):
            os.mkdir(webservices_dir)
        os.chmod(webservices_dir, 0o700)
        self.webservices_dir = webservices_dir

    def p12topem(self):
        p12 = crypto.load_pkcs12(open(self.p12file, 'rb').read(), bytes(self.unlock, 'utf-8'))

        # PEM formatted private key
        key = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12.get_privatekey())

        self.keyfile = os.path.join(self.webservices_dir, self.filebasename + ".key.pem")
        open(self.keyfile, 'a').close()
        os.chmod(self.keyfile, 0o600)
        with open(self.keyfile, 'wb') as f:
            f.write(key)


        # PEM formatted certificate
        cert = crypto.dump_certificate(crypto.FILETYPE_PEM, p12.get_certificate())

        self.certfile = os.path.join(self.webservices_dir, self.filebasename + ".crt.pem")
        open(self.certfile, 'a').close()
        os.chmod(self.certfile, 0o644)
        with open(self.certfile, 'wb') as f:
            f.write(cert)
