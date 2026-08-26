from django.shortcuts import render
from .models import PictureOfWeek


def index(request):
    picture = PictureOfWeek.objects.filter(is_active=True).first()
    return render(request, 'home/index.html', {'picture': picture})
