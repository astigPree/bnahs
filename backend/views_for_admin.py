
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

            schools = models.School.objects.all()

            return JsonResponse({
                'total_schools' : schools.count() if schools else 0,
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 
    

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

            teachers = models.People.objects.filter(role='Teacher')
            
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
            
            teachers = models.People.objects.filter(role='Teacher' , is_evaluated=True)
            
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
                
            teachers = models.People.objects.filter(role='Teacher', is_evaluated=False)

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


@csrf_exempt
def evaluation_submission_rate(request):
    return JsonResponse({
        'message' : 'Not yet implemented',
    }, status=400)
    
@csrf_exempt
def all_teacher_recommendations(request):
    return JsonResponse({
        'message' : 'Not yet implemented',
    }, status=400)


@csrf_exempt
def all_teacher_tenure(request):
    return JsonResponse({
        'message' : 'Not yet implemented',
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
            if not school_id:
                return JsonResponse({
                    'message' : 'School id is required',
                }, status=400)
            
            rejected_school = models.School.objects.filter(id=school_id).first()
            if not rejected_school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
                
            rejected_school.is_accepted = False
            schools = models.School.objects.filter(is_accepted=True).order_by('-created_at')

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
            
            content = request.POST.get('content')
            if not content:
                return JsonResponse({
                    'message' : 'Content is required',
                }, status=400)
            

            # TODO : WAIT FOR UPDATE IN IDENTIFICATION ID OF OBSERVER AND TEACHER
            # Checking if the data is exist before saving
            content : dict = json.loads(content)
            # Matatangap na data sa front end
            """
                {
                    "COT Type" : "Proficient", ! Used to identify what rating type of form
                    "Observer ID" : "Evaluator ID",
                    "Observer Name" : "Evaluator Name", ! Pwede blanko pagpasa
                    "Teacher Name" : "Evaluated Name", ! Pwede blanko pagpasa
                    "Teacher ID" : "Evaluated ID",
                    "Subject & Grade Level" : "Subject & Grade 7",
                    "Date : "September 05, 2023", 
                    "Quarter": "1st Quarter"
                }
            """
            cot_type = content['COT Type']
            observer = content['Observer ID']
            teacher_observed = content['Teacher ID']
            taught = content['Subject & Grade Level'] 
            date = content['Date']
            quarter = content['Quarter']
            
            # Check for evaluator
            search_observer = models.People.objects.filter(employee_id=observer, role='Evaluator').first()
            if not search_observer:
                return JsonResponse({
                    'message' : 'Observer not found',
                }, status=400)
            
            if cot_type == 'Proficient':
                if not my_utils.is_proficient_faculty(search_observer):
                    return JsonResponse({
                        'message' : 'Observer is not a proficient faculty',
                    }, status=400)
            elif cot_type == 'Highly Proficient':
                if not my_utils.is_highly_proficient_faculty(search_observer):
                    return JsonResponse({
                        'message' : 'Observer is not a highly proficient faculty',
                    }, status=400)
            else :
                return JsonResponse({
                    'message' : 'COT type not found',
                }, status=400)
            
            
            search_teacher = models.People.objects.filter(employee_id=teacher_observed , role='Teacher').first()
            if not search_teacher:
                return JsonResponse({
                    'message' : 'Teacher observed not found',
                }, status=400)
            
            
            school = models.School.objects.filter(school_id=search_observer.school_id).first()
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            
            
            my_utils.create_cot_form(
                school=school, 
                observer=search_observer, 
                teacher_observed=search_teacher, 
                subject=taught, 
                cot_date=date, 
                quarter=quarter,
                cot_type=cot_type
            )

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
def create_rpms_folder(request):
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
            
            
            folder_name = request.POST.get('folder_name')
            rpms_folder_school_year = request.POST.get('school_year')
            position_rpms = request.POST.get('position_rpms') # (Proficient and Highly Proficient)
            
            if not folder_name:
                return JsonResponse({
                    'message' : 'Folder name is required',
                    'folder_name' : folder_name,
                }, status=400)
            
            
            if not rpms_folder_school_year:
                return JsonResponse({
                    'message' : 'School year is required',
                    'school_year' : rpms_folder_school_year,
                }, status=400)
                
            if not position_rpms:
                return JsonResponse({
                    'message' : 'Position RPMS is required',
                    'position_rpms' : position_rpms,
                }, status=400)
            
            if position_rpms not in ['Proficient', 'Highly Proficient']:
                return JsonResponse({
                    'message' : 'Position RPMS must be Proficient or Highly Proficient',
                    'position_rpms' : position_rpms,
                }, status=400)
            
            rpms_folder_id = str(uuid4())
            
            rpms_folder = models.RPMSFolder.objects.create(
                rpms_folder_name = folder_name,
                rpms_folder_school_year = rpms_folder_school_year
            )
            rpms_folder.rpms_folder_id = rpms_folder_id
            
            rpms_folder.is_for_teacher_proficient = True if position_rpms == 'Proficient' else False
            
            rpms_folder.save()

            # Create a rpms_classwork folder when the folder is created
            if position_rpms == 'Proficient':
                my_utils.create_rpms_class_works_for_proficient(rpms_folder_id=rpms_folder_id)
            elif position_rpms == 'Highly Proficient':
                my_utils.create_rpms_class_works_for_highly_proficient(rpms_folder_id=rpms_folder_id)
            
            return JsonResponse({
                'message' : 'RPMS folder created successfully',
                'rpms_name' : rpms_folder.rpms_folder_name,
                'rpms_school_year' : rpms_folder.rpms_folder_school_year,
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

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).first()
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

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).first()
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

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS folder not found',
                }, status=400)
                
            rpms_classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpms_folder_id)
            
            
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
                
            # TODO: NAKALIMUTAN KO YUNG SA DEVELOPEMEN PLANS 
            position = request.POST.get('position') # Check what position does the admin want to create for (Proficient or Highly Proficient)
            if not position:
                return JsonResponse({
                    'message' : 'Position is required',
                }, status=400)
            
            schools = models.School.objects.filter(is_accepted=True)
            for school in schools:
                if position == 'Proficient':
                    teachers = models.People.objects.filter(
                        role='Teacher', 
                        school_id=school.school_id, 
                        position__in=my_utils.position['Proficient']
                    )
                    for teacher in teachers:
                        my_utils.create_ipcrf_form_proficient(school=school, teacher=teacher)
                    
                elif position == "Highly Proficient":
                    teachers = models.People.objects.filter(
                        role='Teacher', 
                        school_id=school.school_id, 
                        position__in=my_utils.position['Highly Proficient']
                    )
                    for teacher in teachers:
                        my_utils.create_ipcrf_form_highly_proficient(school=school, teacher=teacher)
                    
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
        


    
    
    