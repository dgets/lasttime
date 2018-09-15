from django.shortcuts import render
from django.http import HttpResponse

from .models import Usage

# Create your views here.

def index(request):
    recent_administrations = Usage.objects.all()
    context = {
        'recent_administrations': recent_administrations,
    }

    return render(request, 'recadm/index.html', context)

def add(request):
    return HttpResponse("Soon there will be shit here...")

def add_new(request):
    return HttpResponse("AhDittoThayat")

def detail(request, usage_id):
    return HttpResponse("Soon there will be code doing shit here, also...")

