
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import People
from django.contrib.auth import authenticate, login, logout
from django.db.models.functions import ExtractYear
from django.db.models import Count

from . import models, my_utils


import secrets
import string
from itertools import groupby
from uuid import uuid4
from threading import Thread
import json





# ================================= Admin Views ============================== # 
@csrf_exempt
def login_admin(request):
    try:
        if request.method == 'POST':
            employee_id = request.POST.get('employee_id')
            password = request.POST.get('password')
            remember_me = request.POST.get('remember_me' , False)
            
            if not employee_id or not password:
                return JsonResponse({
                    'message' : 'Please provide employee_id and password',
                    }, status=400)
            
            user = models.MainAdmin.objects.filter(username=employee_id, password=password).first()
            if not user:
                return JsonResponse({
                    'message' : 'Invalid employee_id or password',
                    }, status=400)
            
            user_authenticated = authenticate(request, username=employee_id, password=password)
            if not user_authenticated:
                return JsonResponse({
                    'message' : 'Invalid employee_id or password',
                    }, status=400)
            
            login(request, user_authenticated)
            if remember_me:
                request.session.set_expiry(1209600) # remember for 14 days
            else:
                request.session.set_expiry(0)
                
            return JsonResponse({
                'message' : 'Login successful',
                }, status=200)
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def add_school(request):
    try:
        if request.method == 'POST':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            school_id = request.POST.get('school_id')
            if not school_id:
                return JsonResponse({
                    'message' : 'Please provide school_id',
                }, status=400)
            
            school = models.School.objects.filter(school_id=school_id).first()
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            

            school.is_accepted = True
            school.action_id = str(uuid4())
            school.save()
            
            user = User.objects.create(
                username=school.email_address,
                password=make_password(school.password),
            )
            
            
            Thread(target=my_utils.send_account_info_email, args=(
                school.email_address, school.email_address, school.password , 'registered-email.html' , settings.EMAIL_HOST_USER, 'School Registration'
                )).start()
            
            return JsonResponse({
                'message' : 'School verified successfully',
            }, status=200)
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_school_inbox(request):
    try:
        if request.method == 'GET':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            school = models.School.objects.all().order_by('-created_at')
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            
            return JsonResponse({
                'school' : [school.get_school_information() for school in school],
            }, status=200)
            
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_all_schools(request):
    try:
        if request.method == 'GET':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            schools = models.School.objects.all().order_by('-created_at')
            if not schools:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            
            return JsonResponse({
                'schools' : [school.get_school_information() for school in schools],
            }, status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_search_schools(request):
    try:
        if request.method == 'POST':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            query = request.POST.get('query')
            if not query:
                return JsonResponse({
                    'message' : 'Please provide query',
                }, status=400)
            
            schools = models.School.objects.filter(school_name__icontains=query)
            if not schools:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            
            return JsonResponse({
                'schools' : [school.get_school_information() for school in schools],
            }, status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_search_schools_by_location(request):
    try:
        if request.method == 'POST':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)

            query = request.POST.get('query')
            if not query:
                return JsonResponse({
                    'message' : 'Please provide query',
                }, status=400)

            schools = models.School.objects.filter(school_address__icontains=query)
            if not schools:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)

            return JsonResponse({
                'schools' : [school.get_school_information() for school in schools],
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



# DASHBOARD 
@csrf_exempt
def get_total_number_of_schools(request):
    try:
        if request.method == 'GET':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)

            all_schools = models.School.objects.all()
            accepted = all_schools.filter(is_accepted=True)
            not_accepted = all_schools.filter(is_accepted=False)

            return JsonResponse({
                'total_schools' : all_schools.count() if all_schools else 0,
                'total_accepted_schools' : accepted.count() if accepted else 0,
                'total_not_accepted_schools' : not_accepted.count() if not_accepted else 0
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 
    

# DASHBOARD
@csrf_exempt
def get_total_number_of_teachers_in_all_school(request):
    try:
        if request.method == 'GET':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)

            teachers = models.People.objects.filter(is_accepted = True, role='Teacher')
            
            return JsonResponse({
                'total_teachers' :  teachers.count() if teachers else 0,
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


# DASHBOARD CALL THIS FIRST
@csrf_exempt
def number_of_evaluation_conducted(request):
    # TODO : DOUBLE CHECK IF IM CORRECT ON THE DATA 
    try:
        if request.method == 'GET':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
              
            teachers = models.People.objects.filter(is_accepted = True, role='Teacher', is_evaluated=True)
            
            return JsonResponse({
                'total_evaluation_conducted' : teachers.count() if teachers else 0,
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
            

# DASHBOARD AFTER ABOVE THEN THIS
@csrf_exempt
def number_of_pending_evaluation(request):
    try:
        if request.method == 'GET':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                
            teachers = models.People.objects.filter(is_accepted = True, role='Teacher', is_evaluated=False)  

            return JsonResponse({
                'total_pending_evaluation' : teachers.count() if teachers else 0,
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

# DASHBOARD AFTER ABOVE THEN THIS
@csrf_exempt
def evaluation_submission_rate(request):
    # Get the number of evaluated teacher each school
    try:
        if request.method == 'GET':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            data = {}
            schools = models.School.objects.filter(is_accepted=True)
            for school in schools:
                data[school.name] = {}
                data[school.name]['teachers'] = models.People.objects.filter(is_accepted = True, school_id=school.school_id, role='Teacher').count()
                data[school.name]['evaluated'] = models.People.objects.filter(is_accepted = True, school_id=school.school_id, role='Teacher', is_evaluated=True).count()
                data[school.name]['pending'] = models.People.objects.filter(is_accepted = True, school_id=school.school_id, role='Teacher', is_evaluated=False).count()
            
            return JsonResponse({
                'data' : data
            }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
        
        
 
@csrf_exempt
def all_teacher_recommendations(request):
    try:
        if request.method == 'GET':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            
            number_of_promotion = 0
            number_of_termination = 0
            number_of_retention = 0
            
            teachers = models.People.objects.filter(is_accepted = True, role='Teacher')
            for teacher in teachers:
                result = my_utils.get_recommendation_result(employee_id=teacher.employee_id)
                if result == 'PROMOTION':
                    number_of_promotion += 1
                elif result == 'TERMINATION':
                    number_of_termination += 1
                elif result == 'RETENTION':
                    number_of_retention += 1
            
            number_of_promotion = number_of_promotion / teachers.count()
            number_of_termination = number_of_termination / teachers.count()
            number_of_retention = number_of_retention / teachers.count()
            
            return JsonResponse({
                'promotion' : number_of_promotion,
                'termination' : number_of_termination,
                'retention' : number_of_retention
            }, status=200)
            
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def get_tenure_of_all_teachers(request):
    try:
        
        if request.method == 'GET':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
        
            people = People.objects.filter( is_accepted = True, role='Teacher')
            total_count = people.count()
            
            if total_count == 0:
                return JsonResponse({
                    '0-3 years': 0,
                    '3-5 years': 0,
                    '5+ years': 0
                }, status=200)

            # Initialize counters
            tenure_counts = {
                '0-3 years': 0,
                '3-5 years': 0,
                '5+ years': 0
            }
             
            for person in people:
                tenure_category = person.get_tenure_category()
                if tenure_category in tenure_counts:
                    tenure_counts[tenure_category] += 1
                    
            
            # Calculate percentages
            tenure_percentages = {
                category: (count / total_count) * 100 for category, count in tenure_counts.items()
            }
            
            return JsonResponse({
                '0-3 years': tenure_percentages['0-3 years'],
                '3-5 years': tenure_percentages['3-5 years'],
                '5+ years': tenure_percentages['5+ years']
            }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    
    
@csrf_exempt
def distribution_ratings(request):
    return JsonResponse({
        'message' : 'Not yet implemented',
    }, status=400)


@csrf_exempt
def reject_school(request):
    try:
        if request.method == 'POST':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            school_id = request.POST.get('school_id')
            reason = request.POST.get('reason')
            if not school_id:
                return JsonResponse({
                    'message' : 'School id is required',
                }, status=400)
                
            if not reason:
                return JsonResponse({
                    'message' : 'Reason is required',
                    'reason' : reason
                }, status=400)
            
            rejected_school = models.School.objects.filter(school_id=school_id).first()
            if not rejected_school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
                
            rejected_school.is_accepted = False
            rejected_school.is_declined = True
            rejected_school.save()
            schools = models.School.objects.filter(is_accepted=True).order_by('-created_at')
            
            Thread(target=my_utils.send_declined_reason, args=(
                rejected_school.email_address, reason  , 'email_declined_school.html' , settings.EMAIL_HOST_USER, 'School Declined', request
                )).start()
            
            return JsonResponse({
                'message' : 'School rejected successfully',
                'schools' : [school.get_school_information() for school in schools],
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 


@csrf_exempt
def create_rating_sheet(request):
    try:
        if request.method == 'POST':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            school_year = request.POST.get('school_year')
            if not school_year:
                return JsonResponse({
                    'message' : 'school_year is required',
                }, status=400)

            
            # quarter = request.POST.get('quarter')
            # if not quarter:
            #     return JsonResponse({
            #         'message' : 'quarter is required [ "Quarter 1" , "Quarter 2" , "Quarter 3" , "Quarter 4" ] ',
            #     }, status=400)

            for_proficient = request.POST.get('type_proficient')
            if not for_proficient :
                return JsonResponse({
                    'message' : 'type_proficient is required [ "Proficient" , "Highly Proficient" ] ',
                }, status=400)
            
            if for_proficient not in ['Proficient', 'Highly Proficient']:
                return JsonResponse({
                    'message' : 'type_proficient is required [ "Proficient" , "Highly Proficient" ] ',
                }, status=400)
            
                        
            if for_proficient == 'Proficient' and models.COTForm.objects.filter(school_year=school_year, is_for_teacher_proficient=True).exists():
                return JsonResponse({
                    'message' : 'School year already exists',
                }, status=400)
            
            if for_proficient == 'Highly Proficient' and models.COTForm.objects.filter(school_year=school_year, is_for_teacher_proficient=False).exists():
                return JsonResponse({
                    'message' : 'School year already exists',
                }, status=400)

            schools = models.School.objects.filter(is_accepted=True)
            if not schools:
                return JsonResponse({
                    'message' : 'Schools not found',
                }, status=400)
                
            for school in schools:
                teachers = models.People.objects.filter(is_accepted = True, role='Teacher', school_id=school.school_id)
                evaluator = models.People.objects.filter(is_accepted = True, role='Evaluator', school_id=school.school_id).first()
                
                for teacher in teachers:
                    #   school : models.School , evaluator : models.People , 
                    #     subject : str , cot_date : str, quarter : str, cot_type : str, 
                    #     school_year : str ):
                    if for_proficient == 'Proficient' and teacher:
                        if my_utils.is_proficient_faculty(teacher):
                            for quarter in [ "Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4" ]:
                                my_utils.create_cot_form(
                                    school=school,
                                    evaluator=evaluator, 
                                    teacher=teacher,
                                    subject='', 
                                    cot_date='', 
                                    quarter=f'{quarter}',
                                    cot_type='Proficient' if my_utils.is_proficient_faculty(teacher) else 'Highly Proficient',
                                    school_year=school_year
                                )
                    elif for_proficient == 'Highly Proficient' and teacher:
                        if my_utils.is_highly_proficient_faculty(teacher):
                            for quarter in [ "Quarter 1", "Quarter 2", "Quarter 3", "Quarter 4" ]:
                                my_utils.create_cot_form(
                                    school=school,
                                    evaluator=evaluator, 
                                    teacher=teacher,
                                    subject='', 
                                    cot_date='', 
                                    quarter=f'{quarter}',
                                    cot_type='Proficient' if my_utils.is_proficient_faculty(teacher) else 'Highly Proficient',
                                    school_year=school_year
                                )
            
            
            # my_utils.create_cot_form(
            #     school=school, 
            #     observer=search_observer, 
            #     teacher_observed=search_teacher, 
            #     subject=taught, 
            #     cot_date=date, 
            #     quarter=quarter,
            #     cot_type=cot_type,
            #     school_year=school_year
            # )

            return JsonResponse({
                'message' : 'Rating sheet created successfully',
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 



@csrf_exempt
def get_all_rpms_folders(request):
    try:
        if request.method == 'GET':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                

            rpms_folders = models.RPMSFolder.objects.all()
            
            return JsonResponse({
                'rpms_folders' : [
                    rpms_folder.get_rpms_folder_information() for rpms_folder in rpms_folders
                ]
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_rpms_folder_by_id(request):
    try:
        if request.method == 'POST':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                

            rpms_folder_id = request.POST.get('rpms_folder_id')
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'RPMS folder id is required',
                }, status=400)

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at').first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS folder not found',
                }, status=400)
            
            return JsonResponse({
                'rpms_folder' : rpms_folder.get_rpms_folder_information()
            }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def update_rpms_folder_background(request):
    try:
        if request.method == 'POST':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                

            rpms_folder_id = request.POST.get('rpms_folder_id')
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'RPMS folder id is required',
                }, status=400)

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at').first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS folder not found',
                }, status=400)

            background_image = request.FILES.get('background_image')
            if not background_image:
                return JsonResponse({
                    'message' : 'Background image is required',
                }, status=400)

            rpms_folder.background_image = background_image
            rpms_folder.save()
            
            return JsonResponse({
                'message' : 'RPMS folder background updated successfully',
            }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_rpms_classworks(request):
    try:
        if request.method == 'POST':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                
            
            rpms_folder_id = request.POST.get('rpms_folder_id')
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'RPMS folder id is required',
                }, status=400)

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at').first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS folder not found',
                }, status=400)
                
            rpms_classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at')
            
            
            return JsonResponse({
                'message' : 'RPMS classworks found successfully',
                'rpms_classworks' : [rpms_classwork.get_rpms_classwork_information() for rpms_classwork in rpms_classworks],
            }, status=200)
                
                
                
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    

@csrf_exempt
def get_rpms_classwork_by_id(request):
    try:
        if request.method == 'POST':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                
            
            rpms_classwork_id = request.POST.get('rpms_classwork_id')
            if not rpms_classwork_id:
                return JsonResponse({
                    'message' : 'RPMS classwork id is required',
                }, status=400)

            rpms_classwork = models.RPMSClassWork.objects.filter(rpms_classwork_id=rpms_classwork_id).order_by('-created_at').first()
            if not rpms_classwork:
                return JsonResponse({
                    'message' : 'RPMS classwork not found',
                }, status=400)
                
            return JsonResponse({
                'message' : 'RPMS classwork found successfully',
                'rpms_classwork' : rpms_classwork.get_rpms_classwork_information(),
            }, status=200)
                
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 


@csrf_exempt
def create_ipcrf_form(request):
    try:
        
        if request.method == 'POST':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                  
            position = request.POST.get('position') # Check what position does the admin want to create for (Proficient or Highly Proficient)
            if not position:
                return JsonResponse({
                    'message' : "'Position is required ['Proficient', 'Highly Proficient']",
                }, status=400)
            
            if position not in ['Proficient', 'Highly Proficient']:
                return JsonResponse({
                    'message' : "Position is invalid ['Proficient', 'Highly Proficient'] ",
                }, status=400)
            
            
            school_year = request.POST.get("school_year")
            if not school_year:
                return JsonResponse({
                    'message' : 'School year is required',
                }, status=400)
            
            if position == 'Proficient' and models.IPCRFForm.objects.filter(school_year=school_year, is_for_teacher_proficient=True).exists():
                return JsonResponse({
                    'message' : 'IPCRF form school_year already exists',
                }, status=400)
            
            if position == 'Highly Proficient' and models.IPCRFForm.objects.filter(school_year=school_year, is_for_teacher_proficient=False).exists():
                return JsonResponse({
                    'message' : 'IPCRF form school_year already exists',
                }, status=400)
            
            schools = models.School.objects.filter(is_accepted=True)
            for school in schools:
                if position == 'Proficient':
                    teachers = models.People.objects.filter(
                        is_accepted = True, 
                        role='Teacher', 
                        school_id=school.school_id, 
                        position__in=my_utils.position['Proficient']
                    )
                    for teacher in teachers:
                        my_utils.create_ipcrf_form_proficient(school=school, teacher=teacher , school_year=school_year)
                    
                elif position == "Highly Proficient":
                    teachers = models.People.objects.filter(
                        is_accepted = True, 
                        role='Teacher', 
                        school_id=school.school_id, 
                        position__in=my_utils.position['Highly Proficient']
                    )
                    for teacher in teachers:
                        my_utils.create_ipcrf_form_highly_proficient(school=school, teacher=teacher,  school_year=school_year)
                    
            return JsonResponse({
                'message' : 'IPCRF form created successfully',
            }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    
@csrf_exempt
def get_number_of_ipcrf_forms(request):
    try:
        if request.method == 'GET':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            number_of_ipcrf_forms = models.IPCRFForm.objects.all().count()
            number_of_iprcf_forms_checked = models.IPCRFForm.objects.filter(is_checked=True).count()
            number_of_ipcrf_forms_not_checked = models.IPCRFForm.objects.filter(is_checked=False).count()
            
                
            return JsonResponse({
                'message' : 'Number of ipcrf forms found successfully',
                'number_of_ipcrf_forms' : number_of_ipcrf_forms,
                'number_of_iprcf_forms_checked' : number_of_iprcf_forms_checked,
                'number_of_ipcrf_forms_not_checked' : number_of_ipcrf_forms_not_checked
                
            }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
        
 
@csrf_exempt
def get_annual_ratings(request):
    try:
        if request.method == 'GET':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            # TODO : IDENTIFY IF THE USER IS EVALUATOR OR NOT
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            schools = models.School.objects.filter(is_accepted=True).order_by('-created_at')
            school_ratings = {}
            for school in schools:
                school_ratings[school.school_id] = {}
                school_ratings[school.school_id]['Name'] = school.name
                teachers = models.People.objects.filter( is_accepted = True, school_id=user.school_id, role='Teacher')
                teacher_ratings = []
                for teacher in teachers: 
                    ipcrf_1 = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id, form_type='PART 1').order_by('-created_at').first()
                    # cot_form = models.COTForm.objects.filter(evaluated_id=teacher.employee_id).order_by('-created_at').first()
                    if ipcrf_1:
                        if my_utils.is_proficient_faculty(teacher):
                            # teacher_ratings.append(my_utils.calculate_scores_for_proficient(ipcrf_1.content_for_teacher , cot_form.content).get('total_score'))
                            teacher_ratings.append(ipcrf_1.rating)
                        else:
                            # teacher_ratings.append(my_utils.calculate_scores_for_highly_proficient(ipcrf_1.content_for_teacher, cot_form.content).get('total_score'))
                            teacher_ratings.append(ipcrf_1.rating)
                    else:
                        teacher_ratings.append(0)
                school_ratings[school.school_id]['Ratings'] = sum(teacher_ratings) / len(teacher_ratings)
            
            """
                {
                    "School ID" : {
                        "Name" : "Name",
                        "Ratings" : 1.85
                    } 
                }
            """
            
            return JsonResponse({
                'school_ratings' : school_ratings
            }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
    }, status=400)



@csrf_exempt
def get_rating_sheet_folder(request , type_proficient : str):
    try:
        if request.method == 'GET':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            # TODO : IDENTIFY IF THE USER IS EVALUATOR OR NOT
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            if not type_proficient :
                return JsonResponse({
                    'message' : 'Must add to url "admin/school/evaluator/get/cot/<str:type_proficient>" is required [ "proficient", "highly_proficient" ] ',
                    }, status=400)
            
            if type_proficient not in ['proficient', 'highly_proficient']:
                return JsonResponse({
                    'message' : 'Must add to url "admin/school/evaluator/get/cot/<str:type_proficient>" is required [ "proficient", "highly_proficient" ] ',
                    }, status=400)
                
            if type_proficient == 'proficient':
                cots = models.COTForm.objects.filter( is_for_teacher_proficient=True)
            else:
                cots = models.COTForm.objects.filter( is_for_teacher_proficient=False) 
            school_year = ""
            school_years = []
            for cot in cots:
                school_year = cot.school_year
                if school_year not in school_years:
                    school_years.append(school_year)
            return JsonResponse({
                'school_years' : school_years
            },status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
    }, status=400)


@csrf_exempt
def get_ipcrf_form_by_admin(request , type_proficient : str ):
    try:
        if request.method == 'GET':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            # TODO : IDENTIFY IF THE USER IS EVALUATOR OR NOT
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            if not type_proficient :
                return JsonResponse({
                    'message' : 'Must add to url "admin/forms/ipcrf/get/<str:type_proficient>/" is required [ "proficient", "highly_proficient" ] ',
                    }, status=400)
            
            if type_proficient not in ['proficient', 'highly_proficient']:
                return JsonResponse({
                    'message' : 'Must add to url "admin/forms/ipcrf/get/<str:type_proficient>/" is required [ "proficient", "highly_proficient" ] ',
                    }, status=400)
                
            if type_proficient == 'proficient':
                ipcrfs = models.IPCRFForm.objects.filter( is_for_teacher_proficient=True , form_type='PART 1')
            else:
                ipcrfs = models.IPCRFForm.objects.filter( is_for_teacher_proficient=False, form_type='PART 1') 
                
            school_year = ""
            school_years = []
            for ipcrf in ipcrfs:
                school_year = ipcrf.school_year
                if school_year not in school_years:
                    school_years.append(school_year)
                    
            return JsonResponse({
                'school_years' : school_years
            },status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
    }, status=400)
