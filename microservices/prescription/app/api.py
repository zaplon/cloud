from flask import Blueprint
from flask import jsonify
from ..soap.client import PrescriptionClient

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/save_prescription')
def save_prescription():
    c = PrescriptionClient()
    result = c.save_prescriptions()
    return jsonify(success=True)
