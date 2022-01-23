from django.urls import path, include
from django.views.generic import RedirectView
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('challenges/', views.challenges, name="challenges"),
    path('challenges/riddles/<int:id>', views.riddle_page, name="riddle_page"),
    path('challenges/wars/<int:id>', views.war_page, name="war_page"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
