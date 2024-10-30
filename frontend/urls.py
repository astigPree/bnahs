
from django.urls import path
from . import views

urlpatterns = [
    path('register/school/verifications/<str:token>/', views.verify_school),
    path('change-password-verifications/<str:token>/', views.verify_changes_password),
]

