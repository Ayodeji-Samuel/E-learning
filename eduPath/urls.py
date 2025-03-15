"""
URL configuration for eduPath project.

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
from django.urls import path, include

urlpatterns = [
    path('admin_dashboard/', include('eduPathCare.urls_admin')),
    path('admin/', admin.site.urls),
    path('', include('eduPathCare.urls')),
    path('summernote/', include('django_summernote.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('trivia/', include('trivia_game.urls', namespace='trivia_game')),
    #path('polls/', include('poll_app.urls', namespace='poll_app')),
    #path('sonar/', include('django_sonar.urls')),
    #path('study-planner/', include('study_planner.urls')),
    path('polls/', include('polls.urls')),
]



from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)