
from django.urls import path
from . import views

urlpatterns = [
    
    # ============= Temporary Path ================
    path('create/admin/', views.create_main_admin),
    
    # ============= General Path ================
    path('user/feeds/', views.get_feeds),
    path('user/notifications/', views.get_notifications),
    path('user/logout/', views.people_logout), # WORKING
    
    path('register/school/', views.register_school), # WORKING
    
    # ============ Admin Path ================
    path('login_admin/', views.login_admin), # WORKING
    path('admin/schools/add/', views.add_school), # WORKING
    path('admin/schools/', views.get_all_schools), # WORKING
    path('admin/schools/search/', views.get_search_schools), # WORKING
    path('admin/schools/inbox/', views.get_school_inbox),  # WORKING
    
    # ============== School Path ================
    path('login_school/', views.login_school), # WORKING
    path('school/register/people/', views.register_people), # WORKING
    path('school/feeds/', views.get_school_feeds), # WORKING
    path('school/post/', views.school_post), # WORKING
    path('school/faculties/', views.get_all_school_faculty), 
    path('school/faculties/search/', views.search_school_faculty),
    path('school/profile/', views.get_school_information), # WORKING
    
    # ============== Evaluator Path ================
    path('login_evaluator/', views.login_evaluator), # WORKING
    path('evaluator/update_profile/', views.people_update_profile),
    path('evaluator/update_education/', views.people_update_education),
    path('evaluator/profile/', views.evaluator_profile),
    
    # =============== Teacher Path ================
    path('login_teacher/', views.login_teacher), # WORKING
    path('teacher/evaluation/', views.teacher_evaluation), 
    path('teacher/form/', views.teacher_forms), # WORKING
    path('teacher/kba/', views.teacher_kba_breakdown), # NEED TO TEST
    path('teacher/recommendations/', views.teacher_recommendations), # NEED TO TEST 
    path('teacher/performance/', views.teacher_performance), # NEED TO TEST
    path('teacher/swot/', views.teacher_swot),
    path('teacher/profile/', views.teacher_profile),
    path('teacher/update_education/', views.people_update_education),
    path('teacher/update_profile/', views.people_update_profile), 
    
]

