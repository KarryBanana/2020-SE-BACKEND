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
    path('getPaperListByKey',views.getPaperListByKey),
    path('login',views.login),
    path('register',views.register),
    path('getPaperListByKeyword',views.getPaperListByKeyword),
    path('getPaperInfoByID',views.getPaperInfoByID),
    path('judgeRepetitiveUserName',views.judgeRepetitiveUserName),
    path('judgeRepetitiveEmail',views.judgeRepetitiveEmail),
    path('check_mail',views.check_mail),
    path('getPaperListByAid',views.getPaperListByAid),
    path('complexSearch',views.complexSearch),
    path('test/', views.responseTest),
    path('follow_author/', views.followAuthor),
    path('collect_paper/', views.collect_paper),
    path('check_user_info/', views.check_user_info),
    path('edit_user_info/', views.edit_user_info),
    path('hot_author/', views.hot_author),
    path('hot_paper/', views.hot_paper),
    path('hot_field/', views.hot_field),
    path('show_collected/', views.collected),
    path('cancel_collect/', views.cancel_collect),
    path('getAuthorInfoById',views.getAuthorInfoById)


              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)