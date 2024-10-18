
from django.urls import path
from . import views

urlpatterns = [
    
    # ============== School Path ================
    path('register_teacher/', views.register_teacher),
    
    # =============== Teacher Path ================
    path('login_teacher/', views.login_teacher),
    path('teacher_dashboard/', views.teacher_dashboard),
    path('teacher_evaluation/', views.teacher_evaluation),
    path('teacher_form/', views.teacher_forms),
    path('teacher_report/', views.teacher_report),
    path('teacher_profile/', views.teacher_profile),
]

