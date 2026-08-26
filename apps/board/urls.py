from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('',              views.board_list,   name='list'),
    path('novy/',         views.board_create, name='create'),
    path('<int:pk>/edit/', views.board_edit,  name='edit'),
    path('<int:pk>/smaz/', views.board_delete, name='delete'),
]
