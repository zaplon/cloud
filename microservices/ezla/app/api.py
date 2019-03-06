from flask import Flask
from client import EZLAClient

app = Flask(__name__)


@app.route("/xml")
def get_xml():
    return EZLAClient.get_xml()
