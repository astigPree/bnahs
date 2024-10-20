
from django.urls import path
from . import views

urlpatterns = [
    
    # ============= General Path ================
    path('user/feeds/', views.get_feeds),
    path('user/notifications/', views.get_notifications),
    path('user/logout/', views.people_logout),
    
    # ============== School Path ================
    path('register_people/', views.register_people),
    path('evaluator_update_profile/', views.people_update_profile),
    path('evaluator_update_education/', views.people_update_education),
    
    # =============== Teacher Path ================
    path('login_teacher/', views.login_teacher),
    path('teacher_evaluation/', views.teacher_evaluation),
    path('teacher_form/', views.teacher_forms),
    path('teacher_kba/', views.teacher_kba_breakdown),
    path('teacher_recommendations/', views.teacher_recommendations),
    path('teacher_performance/', views.teacher_performance),
    path('teacher_swot/', views.teacher_swot),
    path('teacher_profile/', views.teacher_profile),
    path('teacher_update_education/', views.people_update_education),
    path('teacher_update_profile/', views.people_update_profile),
    
]

