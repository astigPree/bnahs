
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
    path('admin/schools/search/location/', views.get_search_schools_by_location),
    path('admin/schools/inbox/', views.get_school_inbox),  # WORKING
    
    path('admin/schools/count/', views.get_total_number_of_schools),
    path('admin/school/teacher/count/', views.get_total_number_of_teachers_in_all_school),
    path('admin/school/teacher/evaluated/count/', views.number_of_evaluation_conducted),
    path('admin/school/teacher/evaluation/pending/count/', views.number_of_pending_evaluation),
    
    path('admin/school/reject/', views.reject_school),
    
    path('admin/school/evaluator/create/cot/', views.create_rating_sheet),
    path('admin/school/evaluator/update/cot/', views.update_rating_sheet),
    
    path('admin/forms/rpms/folders/create/', views.create_rpms_folder),
    path('admin/fomrs/rpms/folder/get/', views.get_rpms_folder_by_id),
    path('admin/forms/rpms/folder/change/image/', views.update_rpms_folder_background),
    path('admin/forms/rpms/folders/', views.get_all_rpms_folders),
    path('admin/forms/rpms/classworks/', views.get_rpms_classworks),
    
    path('admin/forms/ipcrf/create/', views.create_ipcrf_form),
    path('admin/forms/ipcrf/count/', views.get_number_of_ipcrf_forms),
    
    
    # ============== School Path ================
    path('login_school/', views.login_school), # WORKING
    path('school/register/people/', views.register_people), # WORKING
    path('school/feeds/', views.get_school_feeds), # WORKING
    path('school/post/', views.school_post), # WORKING
    path('school/faculties/', views.get_all_school_faculty), 
    path('school/faculties/search/', views.search_school_faculty),
    path('school/profile/', views.get_school_information), # WORKING
    
    path('school/faculties/mention/', views.get_search_school_faculty_for_mentioning),
    path('school/faculties/count/', views.get_number_of_school_faculty),
    path('school/faculties/evaluated/count/', views.get_number_of_school_faculty_evaluated),
    path('school/faculties/evaluated/pending/count/', views.get_number_of_school_faculty_not_evaluated),
    
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

