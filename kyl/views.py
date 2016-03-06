from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render #,get_object_or_404
from django.core.urlresolvers import reverse
#from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
#from django.views.decorators.cache import cache_page #, never_cache
#from django.template.response import TemplateResponse
from django.contrib.auth import authenticate, login , logout
import requests
from politics.settings import GOOGLESECRET_KEY,GOOGLECAPTCHA_URL
from django.contrib import messages


def homepage(request):
    if request.method == 'GET':
        return render(request,"index.html")

def contact(request):
    if request.method == 'GET':
        return render(request,'contact.html')

def rssfeed(request):
    if request.method == "GET":
        dictr = {}
        if request.GET['includess'] != '':
            dictr['includess'] = request.GET['includess']
        if request.GET['excludess'] != '':
            dictr['excludess'] = request.GET['excludess']
        return render(request,'rss.html',dictr)