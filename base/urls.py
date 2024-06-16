from django.urls import path
from . import views as view


urlpatterns = [
    path('', view.getRoutes, name='routes'),
    path('chat/', view.startChat, name='start-chat'),
]