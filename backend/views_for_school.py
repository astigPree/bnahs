
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




    
# ================================= School Views ============================== # 

@csrf_exempt
def register_people(request):
    try:
        # TODO : CHECK IF THE SCHOOL ADMIN IS LOGIN
        if request.method == 'POST':
            
            school_user = models.School.objects.filter(email_address=request.user.username).first()
            if not school_user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            
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
            
            if employee_id in models.People.objects.values_list('employee_id', flat=True):
                return JsonResponse({'status': 'error', 'message': 'Employee ID already exists'}, status=400)

            if not my_utils.parse_date_string(job_started):
                return JsonResponse({'status': 'error', 'message': 'Invalid date format', 'example': 'August 20, 2024'}, status=400)
                    
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
            people.school_id = school_user.school_id
            people.fullname = f'{people.first_name} {people.middle_name} {people.last_name}'
            job_started_date = my_utils.parse_date_string(job_started)
            people.job_started = job_started_date
            
            people.save()

            user = User.objects.create(
                username=employee_id,
                password=make_password(password)
            )

            return JsonResponse({'status': 'success', 'message': 'Faculty record created successfully' }, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Something went wrong : {e}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def login_school(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('employee_id')
            password = request.POST.get('password')
            
            if not email or not password:
                return JsonResponse({
                    'message' : 'Please provide school_id and password',
                    }, status=400)
            
            user = models.School.objects.filter(email_address=email, password=password).first()
            if not user:
                return JsonResponse({
                    'message' : 'Invalid school_id or password',
                    }, status=400)
            
            
            # if not user.is_verified:
            #     return JsonResponse({
            #         'message' : 'School not verified',
            #         }, status=400)
            
            # if not user.is_accepted:
            #     return JsonResponse({
            #         'message' : 'School not accepted, Wait for admin approval',
            #         }, status=400)
            
            
            
            user_authenticated = authenticate(request, username=email, password=password)
            if not user_authenticated:
                return JsonResponse({
                    'message' : 'Invalid school_id or password',
                    }, status=400)
            
            login(request, user_authenticated)
            return JsonResponse({
                'message' : 'Login successful'
                }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_school_information(request):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(email_address=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            return JsonResponse({
                'school' : user.get_school_information()
            },status=200)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_school_feeds(request):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(email_address=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            feeds = {}
            posts = models.Post.objects.filter(post_owner=user.action_id).order_by('-created_at')
            for post in posts:
                comments = models.Comment.objects.filter(post_id=post.post_id).order_by('-created_at')
                attachments = models.PostAttachment.objects.filter(post_id=post.post_id).order_by('-created_at')
                feeds[post.post_id] = {
                    "post" : post.get_post(),
                    "comments" : [comment.get_comment() for comment in comments],
                    "attachments" : [attachment.get_attachment() for attachment in attachments]
                }
                
            return JsonResponse({
                'feeds' : feeds
            },status=200)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def get_school_notifications(request):
    
    return JsonResponse({
        'message' : 'Not yet implemented'
    },status=400)


@csrf_exempt
def school_post(request):
    try:
        if request.method == 'POST':
            
            user = models.School.objects.filter(email_address=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            content = request.POST.get('content')
            
            content_files = []
            try:
                for i in range(5):
                    content_file = request.FILES.get(f'content_file_{i}')
                    if content_file:
                        content_files.append(content_file)
            except Exception as e:
                pass
            
            
            if not content:
                return JsonResponse({
                    'message' : 'Please provide content',
                    }, status=400)
            
            
            post = models.Post.objects.create(
                post_owner=user.action_id,
                content=content,
            )
            
            post.post_id = str(uuid4())
            post.save()
            
            for content_file in content_files:
                models.PostAttachment.objects.create(
                    post_id=post.post_id,
                    attachment=content_file
                )
                
            
            return JsonResponse({
                'message' : 'Post created successfully'
            },status=200)

            
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400)


@csrf_exempt
def get_all_school_faculty(request):
    try:
        if request.method == 'GET':
            
            user = models.School.objects.filter(school_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            people = models.People.objects.filter(school_id=user.school_id).all().order_by('-created_at')
            people_informations = [person.get_information() for person in people]
            
            return JsonResponse({
                'people' : people_informations.append(user.get_school_information())
            },status=200)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400)


@csrf_exempt
def get_number_of_school_faculty(request):
    try:
        if request.method == 'GET':

            user = models.School.objects.filter(school_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)

            people = models.People.objects.filter(school_id=user.school_id, role="Teacher")

            return JsonResponse({
                'number_of_school_faculty' : len(people)
            },status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400)


@csrf_exempt
def get_number_of_school_faculty_evaluated(request):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(school_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)

            people = models.People.objects.filter(school_id=user.school_id, role="Teacher", is_evaluated=True)

            return JsonResponse({
                'number_of_school_faculty_evaluated' : len(people)
            },status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400) 


@csrf_exempt
def get_number_of_school_faculty_not_evaluated(request):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(school_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)

            people = models.People.objects.filter(school_id=user.school_id, role="Teacher", is_evaluated=False)

            return JsonResponse({
                'number_of_school_faculty_evaluated' : len(people)
            },status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400) 
    
    

@csrf_exempt
def search_school_faculty(request):
    try:
        if request.method == 'POST':
            query = request.POST.get('query')
            
            if not query:
                return JsonResponse({
                    'message' : 'Please provide query',
                    }, status=400)
            
            user = models.School.objects.filter(school_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            people = models.People.objects.filter(fullname__icontains=query , school_id=user.school_id).all()
            
            people_information = [person.get_information() for person in people]
            
            return JsonResponse({
                'people' : people_information
            },status=200)
            
            
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400)


@csrf_exempt
def get_search_school_faculty_for_mentioning(request):
    try:
        if request.method == 'POST':
            query = request.POST.get('query')

            if not query:
                return JsonResponse({
                    'message' : 'Please provide query',
                    }, status=400)

            user = models.School.objects.filter(school_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
                
            
            search_people = models.People.objects.filter(school_id=user.school_id, fullname__icontains=query) # Search by name
            if not search_people:
                return JsonResponse({
                    'people' : [],
                },status=200)
            
            return JsonResponse({
                'people' : [person.get_name_and_action_id() for person in search_people],
            },status=200)
                

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400) 





