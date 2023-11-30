from django.views.generic import TemplateView
from django.shortcuts import render
from django.urls import reverse



class IndexView(TemplateView):
    template_name = 'index.html'