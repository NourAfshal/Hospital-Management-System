"""
URL configuration for proj project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib.auth.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from app1.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('patient_register/', AppointmentTemplateView.as_view(), name='patient_register'),
    path('doctor_register/', DoctorTemplateView.as_view(), name='doctor_register'),
    path('nurse_register/', NurseTemplateView.as_view(), name='nurse_register'),
    path('', home, name='home'),
    path('doctor/', doctor, name='doctor'),
    path('nurse/', nurse, name='nurse'),
    path('delete_appointment/<int:appointment_id>/', delete_appointment, name='delete_appointment'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('appointment/', ManageAppointmentTemplateView.as_view(), name='appointment'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
