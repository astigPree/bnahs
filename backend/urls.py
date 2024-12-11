
from django.urls import path
from . import views

urlpatterns = [
    
    # ============= Temporary Path ================
    path('create/admin/', views.create_main_admin),
    
    # ============= General Path ================
    path('user/feeds/', views.get_feeds),
    path('user/notifications/', views.get_notifications),
    path('user/logout/', views.people_logout), # WORKING
    
    path('user/teacher/get/rpms/attachments/', views.get_teacher_all_rpms_attachment),   
    path('user/teacher/get/rpms/attachment/', views.get_teacher_rpms_attachment), 
    
    
    path('register/school/', views.register_school), # WORKING
    path('register/people/', views.register_people), # NEW API
    
    path('user/get/schools/', views.user_get_list_of_schools), # NEW API
    
    path('user/forms/get/cot/', views.get_cot_forms),
    path('user/forms/get/ipcrf/part1/proficient/', views.get_form_for_ipcrf_part_1_proficient),
    path('user/forms/get/ipcrf/part2/', views.get_form_for_ipcrf_part_2),
    path('user/forms/get/ipcrf/part3/', views.get_form_for_ipcrf_part_3),
    path('user/forms/get/ipcrf/part1/highlyproficient/', views.get_form_for_ipcrf_part_1_highly_proficient),
    path('user/forms/get/rpms/proficient/', views.get_rmps_form_proficient),
    path('user/forms/get/cot/', views.get_cot_forms),
    path('user/forms/get/rpms/highlyproficient/', views.get_rmps_form_highly_proficient),
    
    path('user/forgot-password/', views.forgot_password), 
    
    path('user/get/owner/action_id/', views.get_user_by_action_id), # NEW API
    
    path('user/get/info', views.get_what_user),
    
    
    path('user/get/rpms/attachments', views.no_time_get_all_teacher_rpms_attachments),
    path('download/rpms/', views.no_time_download_rpms),
    
    path('user/get/school/years/rpms/', views.get_school_year_kra), 
    path('user/get/school/years/cots/', views.get_school_year_cot),
    path('user/get/school/years/ipcrfs/', views.get_school_year_ipcrf),
    path('user/get/school/years/ipcrfs/all/', views.get_school_year_ipcrf_all),
    
    path('user/react/post/' , views.react_post),
    path('user/comment/post/' , views.comment_post),
    
    
    
    
    
    
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
    
    path('admin/school/submission/rate/', views.evaluation_submission_rate),
    path('admin/school/teachers/tenure/', views.get_tenure_of_all_teachers),
    path('admin/school/teachers/recommendations/', views.all_teacher_recommendations), # NEED TO TEST 
    # TODO : CREATE GET FOR DISTRIBUTIONS RATINGS
    
    path('admin/school/reject/', views.reject_school),
    
    path('admin/school/evaluator/create/cot/', views.create_rating_sheet),
    path('admin/school/evaluator/get/cot/<str:type_proficient>/', views.get_rating_sheet_folder),
    
    path('admin/forms/ipcrf/create/', views.create_ipcrf_form),
    path('admin/forms/ipcrf/count/', views.get_number_of_ipcrf_forms),
    path('admin/forms/ipcrf/get/<str:type_proficient>/' , views.get_ipcrf_form_by_admin),
    
    path('admin/school/teacher/get/annual/ratings/', views.get_annual_ratings),
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # ============== School Path ================
    path('login_school/', views.login_school), # WORKING 
    path('school/register/people/', views.register_people_by_school), # WORKING
    path('school/people/add', views.add_people_by_school), # NEW API
    path('school/feeds/', views.get_school_feeds), # WORKING
    path('school/post/', views.school_post), # WORKING
    path('school/post/notifications/', views.get_school_notifications), # WORKING
    path('school/faculties/', views.get_all_school_faculty), 
    path('school/faculties/search/', views.search_school_faculty),
    path('school/profile/', views.get_school_information), # WORKING
    path('school/summary/', views.school_summary), # WORKING
    
    path('school/faculties/mention/', views.get_search_school_faculty_for_mentioning),
    path('school/faculties/count/', views.get_number_of_school_faculty),
    path('school/faculties/evaluated/count/', views.get_number_of_school_faculty_evaluated),
    path('school/faculties/evaluated/pending/count/', views.get_number_of_school_faculty_not_evaluated),
    
    path('school/teachers/get/tenure/', views.school_get_all_teacher_tenure), # NEED TO TEST 
    path('school/teachers/get/recommendations/', views.school_get_teacher_recommendations), # NEED TO TEST 
    
    path('school/teachers/get/annual/ratings/', views.school_get_annual_ratings),  
    path('school/teachers/get/performance/', views.school_get_performance_true_year),
    path('school/teachers/get/kras/scores/', views.school_get_kras_scores),
    
    
    path('school/forms/rpms/folders/create/', views.create_rpms_folder),
    path('school/forms/rpms/folder/get/', views.get_rpms_folder_by_id),
    path('school/forms/rpms/folder/change/image/', views.update_rpms_folder_background),
    path('school/forms/rpms/folders/<str:type_proficient>/', views.get_all_rpms_folders),
    path('school/forms/rpms/classworks/', views.get_rpms_classworks), 
    path('school/forms/rpms/classwork/get/', views.get_rpms_classwork_by_id),
    
    path('school/forms/cot/get/', views.get_cot_from_school),
    
    path('school/people/reject/', views.reject_people_by_school), # NEW API
    path('school/people/get/by_status/', views.get_all_teacher_by_status),
    
    path('school/get/teachers/', views.get_all_teachers_by_school), # NEW API
    
    path('school/summary/teacher/recommendation/', views.school_summary_recommendations),
    path('school/summary/teacher/tenure/', views.school_summary_performance),
    path('school/summary/teacher/kra/', views.school_summary_rpms),
    path('school/summary/teacher/swot/', views.school_summary_swot),
    
    path('school/generate/report/', views.get_school_report),
    path('school/teacher/generate/report/', views.teacher_generate_report_by_school),
        
    path('school/get/records/cot/', views.school_get_records_cot),
    path('school/get/records/rpms/', views.school_get_records_rpms),
    path('school/get/records/ipcrf/', views.school_get_records_ipcrf),
    path('school/get/cot/', views.get_rating_sheet_by_school),
    
    path('school/get/ipcrf/specific/' , views.school_get_ipcrf),
    
    path("school/faculty/deactivate/", views.deactivate_faculty),
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # ============== Evaluator Path ================
    path('login_evaluator/', views.login_evaluator), # WORKING
    path('evaluator/update_profile/', views.people_update_profile),
    path('evaluator/update_education/', views.people_update_education),
    path('evaluator/profile/', views.evaluator_profile),
    
    path('evaluator/forms/', views.evaluator_forms), 
    path('evaluator/evaluated/', views.evaluator_records), # NEW API
    
    path('evaluator/school/get/teachers/tenure/', views.evaluator_get_all_teacher_tenure), # NEED TO TEST 
    path('evaluator/school/get/teachers/recommendations/', views.evaluator_get_teacher_recommendations), # NEED TO TEST 
    
    path('evaluator/school/get/teachers/annual/ratings/', views.evaluator_get_annual_ratings),  
    path('evaluator/school/get/teachers/performance/', views.evaluator_get_performance_true_year),  
    
    path('evaluator/school/get/all/cot/' , views.get_rating_sheet_for_all_teacher),
    path('evaluator/school/get/cot/', views.get_rating_sheet),
    path('evaluator/school/update/cot/', views.update_rating_sheet),
    
    path('evaluator/school/get/all/ipcrf/part1/', views.get_iprcf_form_for_evaluator_part_1_of_all_teacher),
    path('evaluator/school/get/ipcrf/part1/', views.get_iprcf_form_for_evaluator_part_1_of_teacher),
    path('evaluator/school/check/ipcrf/part1/', views.check_teacher_ipcrf_form_part_1_by_evaluator),
    
    path('evaluator/school/get/all/rpms/folders/', views.evaluator_get_rpms_folders),
    path('evaluator/school/get/rpms/folder/', views.evaluator_get_rpms_folder),
    path('evaluator/school/get/rpms/folder/classwork/', views.evaluator_get_rpms_work),
    path('evaluator/school/get/rpms/folder/classwork/attachments/', views.evaluator_get_rpms_work_attachments),
    path('evaluator/school/get/rpms/attachment/result/', views.evaluator_get_rpms_attachment_result),
    
    path('evaluator/school/check/rpms/attachment/', views.evaluator_check_rpms_attachment),
    path('evaluator/school/get/all/rpms/attachment/', views.evaluator_get_list_of_rpms_takers), 
    
    path('evaluator/school/get/teachers/', views.get_all_teacher_in_school), # NEW API
    
    
    path('evaluator/summary/teacher/recommendation/', views.evaluator_summary_recommendations),
    path('evaluator/summary/teacher/tenure/', views.evaluator_summary_performance),
    path('evaluator/summary/teacher/kra/', views.evaluator_summary_rpms),
    path('evaluator/summary/teacher/swot/', views.evaluator_summary_swot),
    
    path('evaluator/get/records/cot/', views.evaluator_get_records_cot),
    path('evaluator/get/records/rpms/', views.evaluator_get_records_rpms),
    path('evaluator/get/records/ipcrf/', views.evaluator_get_records_ipcrf),
    
    
    path('evaluator/get/ipcrf/specific/' , views.evaluator_get_ipcrf),
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
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
    
    
    path('teacher/school/get/ipcrf/part1/', views.teacher_get_ipcrf_part_1),
    path('teacher/school/update/ipcrf/part1/', views.teacher_update_ipcrf_part_1),
    path('teacher/school/get/ipcrf/part2/', views.teacher_get_ipcrf_part_2),
    path('teacher/school/update/ipcrf/part2/', views.teacher_update_ipcrf_part_2),
    path('teacher/school/get/ipcrf/part3/', views.teacher_get_ipcrf_part_3),
    path('teacher/school/update/ipcrf/part3/', views.teacher_update_ipcrf_part_3),
    
    path('teacher/school/get/rpms/folders/', views.teacher_get_rpms_folders),
    path('teacher/school/get/rpms/folder/', views.teacher_get_rpms_folder),
    path('teacher/school/get/rpms/folder/classwork/', views.teacher_get_rpms_work),
    path('teacher/school/rpms/folder/classwork/turnin/', views.teacher_turn_in_rpms_work),
    path('teacher/school/get/rpms/folder/classwork/attachments/', views.teacher_get_rpms_work_attachments),
    path('teacher/school/get/rpms/folder/classwork/attachments/comment/', views.teacher_private_comment),
    path('teacher/school/get/rpms/attachment/result/', views.teacher_get_rpms_attachment_result),
    path('teacher/school/rpms/folder/classwork/unsubmit/', views.teacher_unsubmit_class_work),
    
    path('teacher/generate/report/', views.teacher_generate_report),
     
    path('teacher/get/records/cot/', views.teacher_get_records_cot),
    path('teacher/get/records/rpms/', views.teacher_get_records_rpms),
    path('teacher/get/records/ipcrf/', views.teacher_get_records_ipcrf),
    
    path('teacher/get/ipcrf/specific/' , views.teacher_get_ipcrf),
     
    path('teacher/forms/cot/get/', views.get_cot_from_by_teacher),
    path('teacher/download/summary/report', views.teacher_download_report)
]

