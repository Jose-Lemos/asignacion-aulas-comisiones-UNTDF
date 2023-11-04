from django.views.generic import TemplateView
from django.shortcuts import render
from django.urls import reverse
from App.models.mapa_de_carreras import *
import requests
from django.db.models import Q
import json
from requests.exceptions import ConnectTimeout
import datetime


class IndexView(TemplateView):
    template_name = 'index.html'