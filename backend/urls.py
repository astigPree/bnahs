
from django.urls import path
from . import views

urlpatterns = [
    
    # ============= General Path ================
    path('user/feeds/', views.get_feeds),
    path('user/notifications/', views.get_notifications),
    path('user/logout/', views.people_logout),
    
    path('register/school/', views.register_school),
    
    
    # ============ Admin Path ================
    path('login_admin/', views.login_admin),
    path('admin/schools/', views.get_all_schools),
    
    
    # ============== School Path ================
    path('login_school/', views.login_school),
    path('school/register/people/', views.register_people),
    path('school/feeds/', views.get_school_feeds),
    path('school/post/', views.school_post),
    path('school/faculties/', views.get_all_school_faculty),
    path('school/faculties/search/', views.search_school_faculty),
    
    # ============== Evaluator Path ================
    path('login_evaluator/', views.login_evaluator),
    path('evaluator/update_profile/', views.people_update_profile),
    path('evaluator/update_education/', views.people_update_education),
    
    # =============== Teacher Path ================
    path('login_teacher/', views.login_teacher),
    path('teacher/evaluation/', views.teacher_evaluation),
    path('teacher/form/', views.teacher_forms),
    path('teacher/kba/', views.teacher_kba_breakdown),
    path('teacher/recommendations/', views.teacher_recommendations),
    path('teacher/performance/', views.teacher_performance),
    path('teacher/swot/', views.teacher_swot),
    path('teacher/profile/', views.teacher_profile),
    path('teacher/update_education/', views.people_update_education),
    path('teacher/update_profile/', views.people_update_profile),
    
]

