"""
URL configuration for smartnoteapi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from notes.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/', include('notes.urls')),
    #to include the URLs from the notes app

    path('api/v1/auth/register/', RegisterView.as_view()),
    path('api/v1/auth/login/',TokenObtainPairView.as_view()),
    #to include the URLs for the browsable API login and logout views
    path('api/v1/auth/refresh/',TokenRefreshView.as_view()),
    
]
