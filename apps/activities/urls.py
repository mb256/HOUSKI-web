from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    path('',               views.activity_list,   name='list'),
    path('novy/',          views.activity_create, name='create'),
    path('<int:pk>/edit/', views.activity_edit,   name='edit'),
    path('<int:pk>/smaz/', views.activity_delete, name='delete'),
]
