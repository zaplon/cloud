from .database import Base
from sqlalchemy import Column, Integer, String


class Prescription(Base):
    __tablename__ = 'prescription'
    id = Column(Integer, primary_key=True)
    external_id = Column(String(256), unique=True)

    def __repr__(self):
        return '<Prescription {}>'.format(self.external_id)
