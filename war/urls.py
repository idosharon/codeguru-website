from django.urls import path, include
from django.views.generic import RedirectView
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.challenges, name="challenges"),
    path('riddles/<int:id>', views.riddle_page, name="riddle_page"),
    path('wars/<int:id>', views.war_page, name="war_page"),
    path('wars/<int:id>/download/<str:filename>',
         views.download, name="war_download"),
]
