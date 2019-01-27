import zipfile
from xml.dom import minidom

from rest_framework.response import Response
from rest_framework.views import APIView

from medicine.models import Prescription, RecipeNumber


