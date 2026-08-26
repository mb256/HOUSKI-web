from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('',                    views.article_list,   name='list'),
    path('<int:pk>/',           views.article_detail, name='detail'),
    path('novy/',               views.article_create, name='create'),
    path('<int:pk>/edit/',      views.article_edit,   name='edit'),
    path('<int:pk>/smaz/',      views.article_delete, name='delete'),
]
