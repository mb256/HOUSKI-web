"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.users.views import HOUSKiPasswordChangeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.home.urls', namespace='home')),
    path('login/',    auth_views.LoginView.as_view(template_name='registration/login.html'),    name='login'),
    path('logout/',   auth_views.LogoutView.as_view(),                                          name='logout'),
    path('password-change/', HOUSKiPasswordChangeView.as_view(), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'
    ), name='password_change_done'),
    path('profil/', include('apps.users.urls', namespace='users')),
    path('nastenka/', include('apps.board.urls', namespace='board')),
    path('clanky/', include('apps.articles.urls', namespace='articles')),
    path('aktivity/', include('apps.activities.urls', namespace='activities')),
    path('kontakty/', include('apps.contacts.urls', namespace='contacts')),
    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
