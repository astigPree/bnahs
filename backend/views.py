
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

from . import models, my_utils , forms_text


import secrets
import string
from itertools import groupby
from uuid import uuid4
from threading import Thread
import json


from .views_for_school import *
from .views_for_admin import *
from .views_for_evaluator import *
from .views_for_teacher import *

# Create your views here.

# ================================= General Views =============================== #

@csrf_exempt
def create_main_admin(request):
    """
        This function only create a a Main Admin, so it must be activated once
    """
    try:
        user = models.MainAdmin.objects.all().first()
        
        
        if user:
            return JsonResponse({
                'message' : 'Main admin already created',
                'employee_id': user.username,
                'password' : user.password
            }, status=400)
            
        admin = models.MainAdmin.objects.create(
            username = 'admin',
            password = 'admin',
        )
        
        user = User.objects.create(
            username=admin.username,
            password=make_password(admin.password),
        )
        
        return JsonResponse({
            'message' : 'Main admin created',
            'employee_id': 'admin',
            'password' : 'admin'
        }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : 'Something went wrong',
            }, status=500)
    


@csrf_exempt
def get_feeds(request):
    """
    This function is used to get the People feeds.
    """
    
    try:
        if request.method == 'GET':  
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            
            
            feeds = {}
            posts = models.Post.objects.filter(post_owner=user.school_action_id).order_by('-created_at')
            for post in posts:
                comments = models.Comment.objects.filter(post_id=post.post_id).order_by('-created_at')
                attachments = models.PostAttachment.objects.filter(post_id=post.post_id).order_by('-created_at')
                feeds[post.post_id] = {
                    "post" : post.get_post(action_id=user.action_id),
                    "comments" : [comment.get_comment() for comment in comments],
                    "attachments" : [attachment.get_attachment() for attachment in attachments]
                }
            
            return JsonResponse({
                'feeds' : feeds
            },status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'message' : 'Something went wrong',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_notifications(request):
    """
        This function is used to get the People notifications.
    """
    
    try:
        if request.method == 'GET':  
            
            user = models.People.objects.filter(username=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            notifications = []
            
            comments = models.Comment.objects.filter(user_id=user.id).order_by('-created_at')
            for comment in comments:
                if comment.is_seen(user.action_id)[0]:
                    notifications.append(comment.get_comment())
            
            
            
            return JsonResponse({
                'notifications' : notifications
            },status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'message' : 'Something went wrong',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    
    
    
@csrf_exempt
def people_update_education(request ):
    if request.method == 'POST':

        try:
            # Update educations if have
            educations = json.loads(request.POST.get('educations'))
            """
                educations = [
                    {
                        'degree' : '',
                        'university' : ''
                    }
                ]
            """
            
            if not educations:
                return JsonResponse({
                    'message' : 'Please provide educations',
                }, status=400)
                
            if educations:
                user = models.People.objects.filter(employee_id=request.user.username).first()
                if not user:
                    return JsonResponse({
                        'message' : 'User not found',
                    }, status=400)
                
                user.update_educations(educations)
                return JsonResponse({
                    'message' : 'Educations updated successfully',
                }, status=200)
                
                
        except Exception as e:
            return JsonResponse({
                'message' : f'Something went wrong : {e}',
                }, status=500)
    
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def people_update_profile(request ):
    if request.method == 'POST':

        user = models.People.objects.filter(employee_id=request.user.username).first()
        based_user = User.objects.filter(username=request.user.username).first()
        
        if not user:
            return JsonResponse({
                'message' : 'User not found',
            }, status=400)
        
        
        try:
            # Update profile if have
            has_changed = False
            firstname = request.POST.get('firstname')
            
            if firstname:
                user.first_name = firstname
                has_changed = True
            
            middlename = request.POST.get('middlename')
            if middlename:
                user.middle_name = middlename
                has_changed = True
            
            lastname = request.POST.get('lastname')
            if lastname:
                user.last_name = lastname
                has_changed = True
            
            jobtitle = request.POST.get('jobtitle')
            if jobtitle:
                user.position = jobtitle
                has_changed = True
            
            department = request.POST.get('department')
            if department:
                user.department = department
                has_changed = True
                
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password and password == confirm_password:
                if based_user:
                    pass
                    
                    # TODO : Change password
                has_changed = True    
                
            
            
            if has_changed:
                # Re-authenticate the user with the new credentials
                old_based_user = User.objects.get(username=user.employee_id)
                old_based_user.set_password(user.password if not password else password)  # Use the raw user_key here
                old_based_user.save()
                new_user = authenticate(username=user.employee_id, password=user.password)
                if new_user:
                    login(request, new_user)
                    user.save()
                    
                return JsonResponse({
                    'message' : 'Profile updated successfully',
                }, status=200)
            
            return JsonResponse({
                'message' : 'No changes made',
            }, status=200)
            
                
        except Exception as e:
            return JsonResponse({
                'message' : f'Something went wrong : {e}',
                }, status=500)
    
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

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
            
            teachers = models.People.objects.filter(role="Teacher", school_id=user.school_id)
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
                user = models.People.objects.filter(email_address=email).first()
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

