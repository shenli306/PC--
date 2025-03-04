from django.urls import path
from . import views

urlpatterns = [
    path('neicun/', views.get_memories, name='neicun'),
] 