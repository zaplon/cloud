from .database import Base as db


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(256), unique=True)

    def __repr__(self):
        return '<Prescription {}>'.format(self.external_id)
