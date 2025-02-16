"""
URL configuration for Django project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from PAC.views import *
from PAC import views
from django.conf.urls import handler404, handler500

urlpatterns = [
    path("zyd/", admin.site.urls),
    path("", login),
    path("index/", index, name='index'),
    path("autowx/", autowx),
    path("contact/", contact, name='contact'),
    path("about/", about, name='about'),
    path("login/", login, name='login'),
    path("register/", register, name='register'),
    path("zero/", zero),
    path("CPU/", cpu_view, name='cpu'),
    path("xianka/", views.xianka, name='xianka'),
    path("zhuban/", views.zhuban, name='zhuban'),
    path("neicun/", views.neicun, name='neicun'),
    path("yingpan/", views.yingpan, name='yingpan'),
    path("dianyuan/", views.dianyuan, name='dianyuan'),
    path("logout/", views.logout_view, name='logout'),
]

handler404 = 'PAC.views.custom_404'
handler500 = 'PAC.views.custom_500'
