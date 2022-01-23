from django.urls import path, include
from django.views.generic import RedirectView
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name="index"),
    path('group/', views.group, name="group"),
    path('accounts/profile/', views.profile, name="profile"),
    path('accounts/profile/delete', views.delete_profile, name="delete_profile"),
    path('accounts/register/', views.register, name="register"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('invite/create', views.create_invite, name="invite_create"),
    path('invite/<str:code>', views.invite, name="invite"),
    path('invite/', RedirectView.as_view(pattern_name='index', permanent=True)),
    path('group/leave', views.leave_group, name="leave_group"),
    path('set_lang', views.set_lang, name="set_language"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
