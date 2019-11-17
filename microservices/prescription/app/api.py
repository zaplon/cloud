import json

from flask import Blueprint, current_app
from flask import jsonify, request
from flask_cors import CORS
from flask_inputs import Inputs
from flask_inputs.validators import JsonSchema
from soap.client import PrescriptionClient

bp = Blueprint('api', __name__, url_prefix='/api')
CORS(bp, headers='Content-Type')


@bp.route('/test/', methods=['POST'])
def test():
    data = json.loads(request.data)
    c = PrescriptionClient(data)
    if c.test_connection():
        return jsonify(success=True)
    else:
        return "<h1>Error</h1>", 400


@bp.route('/sign_prescription/', methods=['POST'])
def sign_prescription():
    inputs = ValidateJsonInputs(request)
    if not inputs.validate():
        current_app.logger.info(inputs.errors)
        return jsonify(success=False, errors=inputs.errors)
    return PrescriptionClient.sign_prescription_from_string(request.data['data'])


def json_response(data={}, status_code=200):
    return current_app.response_class(
        response=json.dumps(data),
        status=status_code,
        mimetype='application/json'
    )


@bp.route('/cancel_prescription/', methods=['POST'])
def cancel_prescription():
    data = json.loads(request.data)
    c = PrescriptionClient(data['profile'])
    status = c.cancel_prescription(data)
    return json_response({}, status_code=200 if status else 400)


@bp.route('/save_prescription/', methods=['POST'])
def save_prescription():
    inputs = SaveJsonInputs(request)
    if not inputs.validate():
        current_app.logger.info(inputs.errors)
        return json_response(inputs.errors, status_code=400)
    data = json.loads(request.data)
    c = PrescriptionClient(data['profile'])
    status, result = c.save_prescriptions(data)
    current_app.logger.info(result)
    status_code = 200 if status else 400
    return json_response(result, status_code)


save_schema = {
    'type': 'object',
    'properties': {
        'pajent': {'type': 'object'},
        'leki': {'type': 'array'},
        'recepta': {'type': 'object'},
        'profile': {'type': 'object'}
    }
}


class SaveJsonInputs(Inputs):
    json = [JsonSchema(schema=save_schema)]


validate_schema = {
    'type': 'object',
    'properties': {
        'data': {'type': 'string'}
    }
}


class ValidateJsonInputs(Inputs):
    json = [JsonSchema(schema=validate_schema)]
