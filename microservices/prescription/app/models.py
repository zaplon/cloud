from .database import Base
from sqlalchemy import Column, Integer, String


class Prescription(Base):
    __tablename__ = 'prescription'
    id = Column(Integer, primary_key=True)
    external_id = Column(String(256), unique=True)

    def __repr__(self):
        return '<Prescription {}>'.format(self.external_id)


# class Profile(Base):
#     __tablename__ = 'profile'
#     user_id = Column(Integer, unique=True)
#     rola_biznesowa = Column(String(128))
#     certificate_tls = Column(String(256))
#     certificate_tls_password = Column(String(32))
#     certificate_wsse = Column(String(256))
#     certificate_wsse_password = Column(String(32))
#     certificate_user = Column(String(256))
#     certificate_user_password = Column(String(32))
#
#     id_podmiotu_oid_ext = Column(String(128))
#     id_podmiotu_lokalne = Column(String(128))
#     id_pracownika_oid_ext = Column(String(32))
#     id_miejsca_pracy_oid_ext = Column(String(8))
