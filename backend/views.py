
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import People
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.db.models.functions import ExtractYear
from django.db.models import Count

from django.http import FileResponse, HttpResponse, Http404 
from django.conf import settings
import os


from . import models, my_utils , forms_text


import secrets
import string
from itertools import groupby
from uuid import uuid4
from threading import Thread
import json


from .views_for_school import *
from .views_for_school_2 import *
from .views_for_school_3 import *

from .views_for_admin import *
from .views_for_admin_2 import *

from .views_for_evaluator import *
from .views_for_evaluator_2 import *

from .views_for_teacher import * 
from .views_for_teacher_2 import *
from .views_for_teacher_3 import *

from .views_2 import *
from .views_3 import *

# Create your views here.

# ================================= General Views =============================== #


@csrf_exempt
def people_logout(request ):
    try:
        if request.method == 'POST':
            logout(request)
            return JsonResponse({
                'message' : 'Logout successful'
                }, status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_people_all_rpms_folders(request):
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
            if not rpms_folders:
                return JsonResponse({
                    'message' : 'No rpms folders found',
                }, status=400)
            
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
def get_people_rpms_classworks(request):
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
            if not rpms_classworks:
                return JsonResponse({
                    'message' : 'RPMS classworks not found',
                }, status=400)
            
            
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
def get_all_teachers(request):
    try:
        if request.method == 'GET':
            user = models.People.objects.filter(employee_id=request.user.username, role="Evaluator").first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            teachers = models.People.objects.filter(is_accepted = True, role="Teacher", school_id=user.school_id)
            if not teachers:
                return JsonResponse({
                    'message' : 'No teachers found',
                }, status=400)
            
            return JsonResponse({
                'teachers' : [teacher.get_information() for teacher in teachers]
            }, status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400 )


@csrf_exempt
def get_teacher_all_rpms_attachment(request):
    try:
        if request.method == 'POST':
            user = request.user.is_authenticated
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            teacher_id = request.POST.get('teacher_id')
            
            rpms_attachments = models.RPMSAttachment.objects.filter(employee_id=teacher_id).order_by('-created_at')
            if not rpms_attachments:
                return JsonResponse({
                    'message' : 'RPMS attachments not found',
                }, status=400)
            
            return JsonResponse({
                'rpms_attachments' : [rpms_attachment.get_information() for rpms_attachment in rpms_attachments],
            }, status=200)
    
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def get_teacher_rpms_attachment(request):
    try:
        
        if request.method == 'POST':
            user = request.user.is_authenticated
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            attachment_id = request.POST.get('rpms_attachment_id')
            if not attachment_id:
                return JsonResponse({
                    'message' : 'RPMS attachment id is required',
                }, status=400)
            
            rpms_attachment = models.RPMSAttachment.objects.filter(attachment_id=attachment_id).order_by('-created_at').first()
            if not rpms_attachment:
                return JsonResponse({
                    'message' : 'RPMS attachment not found',
                }, status=400)
            
            return JsonResponse({
                'rpms_attachment' : rpms_attachment.grade
            }, status=200)
    
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    

@csrf_exempt
def get_form_for_ipcrf_part_1_proficient(request):
    try:
        if request.method == 'GET':
            return JsonResponse({
                'form' : forms_text.form_for_ipcrf_part_1_proficient()
            },status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_form_for_ipcrf_part_1_highly_proficient(request):
    try:
        if request.method == 'GET':
            return JsonResponse({
                'form' : forms_text.form_for_ipcrf_part_1_highly_proficient()
            },status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def get_form_for_ipcrf_part_2(request):
    try:
        if request.method == 'GET':
            return JsonResponse({
                'form' : forms_text.form_for_ipcrf_part_2_proficient()
            },status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_form_for_ipcrf_part_3(request):
    try:
        if request.method == 'GET':
            return JsonResponse({
                'form' : forms_text.form_for_ipcrf_part_2_proficient()
            },status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_rmps_form_proficient(request):
    try:
        if request.method == 'GET':
            return JsonResponse({
                'kra1' : forms_text.form_for_kra1_proficient(),
                'kra2' : forms_text.form_for_kra2_proficient(),
                'kra3' : forms_text.form_for_kra3_proficient(),
                'kra4' : forms_text.form_for_kra4_proficient(),
                'plus_factor' : forms_text.form_for_plus_factor_proficient()
            },status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_rmps_form_highly_proficient(request):
    try:
        if request.method == 'GET':
            return JsonResponse({
                'kra1' : forms_text.form_for_kra1_highly_proficient(),
                'kra2' : forms_text.form_for_kra2_highly_proficient(),
                'kra3' : forms_text.form_for_kra3_highly_proficient(),
                'kra4' : forms_text.form_for_kra4_highly_proficient(),
                'plus_factor' : forms_text.form_for_plus_factor_highly_proficient()
            },status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_cot_forms(request):
    try:
        if request.method == 'GET':
            return JsonResponse({
                'proficient' : forms_text.form_cot_proficient(),
                'highly_proficient' : forms_text.form_cot_highly_proficient()
            },status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def forgot_password(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('email')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if not email:
                return JsonResponse({
                   'message' : 'Email is required',
                   'email' : email
                }, status=400)
            
            if not new_password:
                return JsonResponse({
                   'message' : 'New password is required',
                   'new_password' : new_password
                }, status=400)
                
            if not confirm_password:
                return JsonResponse({
                   'message' : 'Confirm password is required',
                   'confirm_password' : confirm_password
                }, status=400)
            
            if new_password != confirm_password:
                return JsonResponse({
                   'message' : 'Passwords do not match',
                   'new_password' : new_password,
                   'confirm_password' : confirm_password
                }, status=400)
                
            user_type = None
            user = models.School.objects.filter(email_address=email).first()
            
            if user is None:
                user = models.People.objects.filter(is_accepted = True, email_address=email).first()
                if user is None:
                    return JsonResponse({
                        'message' : 'User not found',
                        'email' : email
                    }, status=400)
                else:
                    user_type = 'people'
            else :
                user_type ='school'
                
            verification_link = models.VerificationLink.generate_change_key_link(email, {
                'password' : new_password, 'confirm_password' : confirm_password , 'user_type' : user_type
            })

            # Send password reset link to user's email
            Thread(target=my_utils.send_password_reset_email, args=(
                user.email_address, verification_link , 'forgot_password.html', settings.EMAIL_HOST_USER, 'Bnahs Change Password' , request
            )).start()
            

            return JsonResponse({
                'message' : 'Password reset link sent successfully',
            }, status=200)


    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def get_user_by_action_id(request):
    try:
        if request.method == 'POST':
            action_id = request.POST.get('action_id')
            
            if not action_id:
                return JsonResponse({
                   'message' : 'Action ID is required',
                   'action_id' : action_id
                }, status=400)
            
            data = None
            user_type = None
            user = models.MainAdmin.objects.filter(action_id=action_id).first()
            if user:
                user_type = 'MainAdmin'
                data = None
            if not user:
                user = models.School.objects.filter(action_id=action_id).first()
                if user:
                    user_type = 'School'
                    data = user.get_school_information()
                if not user:
                    user = models.People.objects.filter(action_id=action_id).first()
                    if user:
                        user_type = user.role
                        data = user.get_information()
                    if not user:
                        return JsonResponse({
                            'message' : 'User not found',
                            'action_id' : action_id
                        }, status=400)
             
            return JsonResponse({ 
                'action_id' : action_id,
                'data' : data,
                'user' : user_type
            }, status=400)
             
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 


@csrf_exempt
def register_school(request):
    try:
        if request.method == 'POST':
            name = request.POST.get('name')
            school_id = request.POST.get('school_id')
            school_name = request.POST.get('school_name')
            school_address = request.POST.get('school_address')
            school_type = request.POST.get('school_type')
            contact_number = request.POST.get('contact_number')
            email_address = request.POST.get('email_address')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            school_logo = request.FILES.get('school_logo')

            if password != confirm_password:
                return JsonResponse({'status': 'error', 'message': 'Passwords do not match'}, status=400)
            
            verification =  models.VerificationLink.objects.filter(email=email_address).first()
            
            if verification:
                if not verification.is_expired():
                    return JsonResponse({'message': 'Please check your email or wait for 30 mins'})
                else :
                    verification.delete()
                    school = models.School.objects.filter(email_address=email_address).first()
                    if school:
                        school.delete()
                
            
            # Check if the already school exist
            if models.School.objects.filter(email_address=email_address).exists():
                return JsonResponse({ 'message': 'School already exists'}, status=400)

            if models.School.objects.filter(school_id=school_id).exists():
                return JsonResponse({ 'message': 'School ID already exists'}, status=400)
            
            if models.People.objects.filter(email_address=email_address , school_id=school_id).exists():
                return JsonResponse({ 'message': 'School Email already exists'}, status=400)

            school = models.School.objects.create(
                name=name,
                school_id=school_id,
                school_name=school_name,
                school_address=school_address,
                school_type=school_type,
                contact_number=contact_number,
                email_address=email_address,
                password=password,
            )
            
            if school_logo:
                school.school_logo = school_logo
            
            school.action_id = str(uuid4())
            school.save()
            
            verification = models.VerificationLink.generate_link(email_address)
            
            # verification_code , template , masbate_locker_email , subject
            Thread(target=my_utils.send_verification_email, args=(
                email_address, verification , 'email-template.html', settings.EMAIL_HOST_USER, 'School Registration' , request
            )).start()
            

            return JsonResponse({
                'status': 'success',
                'message': 'Check your email for verification link in order to activate your account',
            },status=200)
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)



@csrf_exempt
def register_people(request):
    try:
        if request.method == 'POST':
            # employee_id = request.POST.get('employee_id')
            # school_id = request.POST.get('school_id')
            # school_name = request.POST.get('school_name')
            # school_address = request.POST.get('school_address')
            # school_type = request.POST.get('school_type')
            # contact_number = request.POST.get('contact_number')
            # email_address = request.POST.get('email_address')
            # password = request.POST.get('password')
            # confirm_password = request.POST.get('confirm_password')
            # school_logo = request.FILES.get('school_logo')
            
            role = request.POST.get('role')
            school_id = request.POST.get('school_id')
            employee_id = request.POST.get('employee_id')
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            email_address = request.POST.get('email_address')
            position = request.POST.get('position')
            job_started = request.POST.get('job_started')
            grade_level = request.POST.get('grade_level')
            department = request.POST.get('department')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')


            if password != confirm_password:
                return JsonResponse({'status': 'error', 'message': 'Passwords do not match'}, status=400)
            
            if not my_utils.parse_date_string(job_started):
                return JsonResponse({'status': 'error', 'message': 'Invalid date format'}, status=400)
            school = models.School.objects.filter(school_id=school_id).first()
            if not school:
                return JsonResponse({ 'message': 'School does not exist'}, status=400)
            
            # Check if the already people exist
            if models.School.objects.filter(email_address=email_address).exists():
                return JsonResponse({ 'message': 'People Email already exists'}, status=400)
            
            if models.People.objects.filter(email_address=email_address , role=role).exists():
                return JsonResponse({ 'message': 'People Email already exists'}, status=400)

            if models.People.objects.filter(employee_id=employee_id, school_id=school.school_id , role=role).exists():
                return JsonResponse({ 'message': 'People ID already exists'}, status=400)
            
            
            # verification =  models.VerificationLink.objects.filter(email=email_address).first()
            
            # if verification:
            #     if not verification.is_expired():
            #         return JsonResponse({'message': 'Please check your email or wait for 30 mins'})
            #     else :
            #         verification.delete()
            #         school = models.People.objects.filter(email_address=email_address).first()
            #         if school:
            #             school.delete()
            
            people = People.objects.create(
                role=role,
                school_id=school_id,
                employee_id=employee_id,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                email_address=email_address,
                position=position,
                grade_level=grade_level,
                department=department,
                password=password,  # Storing plain password temporarily
            )
            
            people.action_id = str(uuid4())
            people.school_id = school_id
            people.fullname = f'{people.first_name} {people.middle_name} {people.last_name}'
            job_started_date = my_utils.parse_date_string(job_started)
            people.job_started = job_started_date
            
            # verification.delete()
            
            
            people.is_verified = True # Remove for testing only 
            people.save()
            
             
            # verification = models.VerificationLink.generate_link(email_address)
            
            # # verification_code , template , masbate_locker_email , subject
            # Thread(target=my_utils.send_verification_email, args=(
            #     email_address, verification , 'email-template.html', settings.EMAIL_HOST_USER, f'{role} Registration' , request
            # )).start()
            

            return JsonResponse({
                'status': 'success',
                'message': 'Check your email for verification link in order to activate your account',
            },status=200)
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def user_get_list_of_schools(request):
    try:
        if request.method == 'GET':
            schools = models.School.objects.filter(is_accepted=True).order_by('-created_at')
            return JsonResponse({
                'schools' : [school.get_school_information() for school in schools],
            },status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)







# =================NO time
@csrf_exempt
def no_time_get_all_teacher_rpms_attachments(request):
    try:
        if request.method == 'POST':
            
            teacher_id = request.POST.get("teacher_id")
            
            
            if not teacher_id:
                return JsonResponse({
                   'message' : 'Teacher ID is required',
                   'teacher_id' : teacher_id
                }, status=400)
            
            
            teacher = models.People.objects.filter(employee_id=teacher_id).first()
            if not teacher:
                return JsonResponse({
                   'message' : 'Teacher does not exist',
                   'teacher_id' : teacher_id
                }, status=400)
            
            rpms_data = {
                
            }
            rpms_folders = models.RPMSFolder.objects.filter(school_id=teacher.school_id).order_by('-created_at')
            for folder in rpms_folders:
                class_works = models.RPMSClassWork.objects.filter(rpms_folder_id=folder.rpms_folder_id).order_by('-created_at')
                for class_work in class_works:
                    if class_work.title not in rpms_data:
                        rpms_data[class_work.title] = []
                    attachment = models.RPMSAttachment.objects.filter(class_work_id=class_work.class_work_id).order_by('-created_at').first()
                    if attachment:
                        rpms_data[class_work.title].append(attachment.get_information())
                        
            return JsonResponse(rpms_data, status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def no_time_download_rpms(request):
    try:
        if request.method == "POST":
            rpms_id = request.POST.get('rpms_id')
            if not rpms_id:
                return JsonResponse({
                    'message' : 'RPMS ID is required',
                    'rpms_id' : rpms_id
                }, status=400)
                
            rpms_attachment = models.RPMSAttachment.objects.filter(attachment_id=rpms_id).first()
            if not rpms_attachment:
                return JsonResponse({
                    'message' : 'RPMS attachment not found',
                    'rpms_id' : rpms_id
                }, status=400)
                
            attachment = rpms_attachment
            index = request.POST.get('index') 
                
            if index == "1":
                file_path = os.path.join(settings.MEDIA_ROOT, attachment.file.name)
            elif index == "2":
                file_path = os.path.join(settings.MEDIA_ROOT, attachment.file2.name)
            elif index == "3":
                file_path = os.path.join(settings.MEDIA_ROOT, attachment.file3.name)
            elif index == "4":
                file_path = os.path.join(settings.MEDIA_ROOT, attachment.file4.name)
            else :
                return JsonResponse({
                    'message' : 'index not found',
                }, status=400)
            
            if os.path.exists(file_path):
                response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename={os.path.basename(file_path)}'
                return response
            else:
                return JsonResponse({
                    'message' : 'RPMS attachment not found',
                    'rpms_id' : rpms_id
                }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    



