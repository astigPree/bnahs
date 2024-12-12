
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
            
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            school = models.School.objects.filter(school_id=user.school_id).first()
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            
            
            feeds = {}
            posts = models.Post.objects.filter(post_owner=school.action_id).order_by('-created_at')
            for post in posts:
                comments = models.Comment.objects.filter(post_id=post.post_id).order_by('created_at')
                attachments = models.PostAttachment.objects.filter(post_id=post.post_id).order_by('-created_at')
                feeds[post.post_id] = {
                    "post" : post.get_post(action_id=user.action_id),
                    "comments" : [comment.get_comment(action_id=user.action_id) for comment in comments],
                    "attachments" : [attachment.get_attachment() for attachment in attachments]
                }
            
            return JsonResponse(feeds,status=200)
            
            
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
            
            user = models.People.objects.filter(is_deactivated = False, username=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            notifications = []
            
            comments = models.Comment.objects.filter(user_id=user.id).order_by('-created_at')
            for comment in comments:
                if comment.is_seen_by(user.action_id)[0]:
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
                user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
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


# @csrf_exempt
# def people_update_profile(request ):
#     if request.method == 'POST':

#         user = models.People.objects.filter(employee_id=request.user.username).first()
#         based_user = User.objects.filter(username=request.user.username).first()
        
#         if not user:
#             return JsonResponse({
#                 'message' : 'User not found',
#             }, status=400)
        
        
#         try:
#             # Update profile if have
#             has_changed = False
#             firstname = request.POST.get('firstname')
            
#             if firstname:
#                 user.first_name = firstname
#                 has_changed = True
            
#             middlename = request.POST.get('middlename')
#             if middlename:
#                 user.middle_name = middlename
#                 has_changed = True
            
#             lastname = request.POST.get('lastname')
#             if lastname:
#                 user.last_name = lastname
#                 has_changed = True
            
#             jobtitle = request.POST.get('jobtitle')
#             if jobtitle:
#                 user.position = jobtitle
#                 has_changed = True
            
#             department = request.POST.get('department')
#             if department:
#                 user.department = department
#                 has_changed = True
                
#             password = request.POST.get('password')
#             confirm_password = request.POST.get('confirm_password')
#             if password and password == confirm_password:
#                 if based_user:
#                     # pass
#                     user.password = password
#                     # TODO : Change password
#                 has_changed = True    
            
#             profile = request.FILES.get('profile')
#             if profile:
#                 user.profile = profile
#                 has_changed = True
            
            
            
#             if has_changed:
#                 # Re-authenticate the user with the new credentials
#                 based_user.set_password(user.password if not password else password)  # Use the raw user_key here
#                 based_user.save()
#                 new_user = authenticate(username=user.employee_id, password=user.password)
#                 if new_user:
#                     login(request, new_user)
#                     user.save()
                    
#                 return JsonResponse({
#                     'message' : 'Profile updated successfully',
#                 }, status=200)
            
#             return JsonResponse({
#                 'message' : 'No changes made',
#             }, status=200)
            
                
#         except Exception as e:
#             return JsonResponse({
#                 'message' : f'Something went wrong : {e}',
#                 }, status=500)
    
        
#     return JsonResponse({
#         'message' : 'Invalid request',
#         }, status=400)



@csrf_exempt
def people_update_profile(request):
    if request.method == 'POST':
        user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
        based_user = User.objects.filter(username=request.user.username).first()
        
        if not user or not based_user:
            return JsonResponse({
                'message': 'User not found',
            }, status=400)
        
        try:
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
                user.password = password
                based_user.set_password(password)
                based_user.save()
                update_session_auth_hash(request, based_user)  # Important to keep the user authenticated after password change
                has_changed = True    
            
            profile = request.FILES.get('profile')
            if profile:
                user.profile = profile
                has_changed = True
            
            if has_changed:
                user.save()
                return JsonResponse({
                    'message': 'Profile updated successfully',
                }, status=200)
            
            return JsonResponse({
                'message': 'No changes made',
            }, status=200)
        
        except Exception as e:
            return JsonResponse({
                'message': f'Something went wrong: {e}',
            }, status=500)
    
    return JsonResponse({
        'message': 'Invalid request',
    }, status=400)




@csrf_exempt
def get_what_user(request):
    try:
        if request.method == 'GET':
            
            admin = models.MainAdmin.objects.filter(username=request.user.username).first()
            if admin:
                return JsonResponse({
                    'role': 'admin',
                    'data' : {}
                }, status=200)
                
            school = models.School.objects.filter(email_address=request.user.username).first()
            if school:
                return JsonResponse({
                    'role': 'school_admin',
                    'data' : school.get_school_information()
                }, status=200)
            
            teacher = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
            if teacher:
                return JsonResponse({
                    'role': 'teacher',
                    'data': teacher.get_information()
                }, status=200)
            
            return JsonResponse({
                'role': 'invalid'
            }, status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400)






