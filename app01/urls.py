from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.template.context_processors import static
from django.urls import path, include, re_path

from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('test/',views.responseTest),
    path('getPaperInfoByKey',views.getPaperInfoByKey),
    path('login',views.login),
    path('register',views.register),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)