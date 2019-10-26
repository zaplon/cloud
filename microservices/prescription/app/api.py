from flask import Blueprint, current_app
from flask import jsonify, request
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from soap.client import PrescriptionClient

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/save_prescription/')
def save_prescription():
    inputs = JsonInputs(request)
    if not inputs.validate():
        current_app.logger.info(inputs.errors)
        return jsonify(success=False, errors=inputs.errors)
    c = PrescriptionClient()
    result = c.save_prescriptions(request.data)
    current_app.logger.info(result)
    return jsonify(success=True, data=result)


schema = {
    'type': 'object',
    'properties': {
        'pajent': {'type': 'object'},
        'leki': {'type': 'array'},
        'recepta': {'type': 'object'}
    }
}


class JsonInputs(Inputs):
    json = [JsonSchema(schema=schema)]
