
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import People
from django.contrib.auth import authenticate, login, logout 
from datetime import datetime, timedelta
from django.utils import timezone 

from . import models, my_utils


import secrets
import string
from itertools import groupby
from uuid import uuid4
from threading import Thread
import json






@csrf_exempt
def get_all_school_faculty_by_evaluator(request):
    try:
        if request.method == 'GET':
             
                        
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                   'message' : 'User not found',
                    }, status=400)
             
            people = models.People.objects.filter(is_accepted = True, school_id=user.school_id).order_by('-created_at')
            people_informations = [person.get_information() for person in people]
            school = models.School.objects.filter(school_id=user.school_id).first()
            people_informations.append(school.get_school_information())
            return JsonResponse({
                'people' : people_informations
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
def get_school_notifications_by_evaluator(request):
    try:
        if request.method == "GET":

            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)

            notifications = models.Notifications.objects.filter( 
                notification_type="POST",
                action_id = user.action_id
            ).order_by('-created_at')

            return JsonResponse({
                'notifications' : [notification.get_notification_by_array() for notification in notifications]
            })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)




@csrf_exempt
def evaluator_private_comment(request):
    try:
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            attachment_id = request.POST.get('attachment_id')
            comment = request.POST.get('comment')
            if not attachment_id:
                return JsonResponse({
                    'message' : 'Attachment ID is required',
                }, status=400)
                
            if not comment:
                return JsonResponse({
                    'message' : 'Comment is required',
                }, status=400)
                
            attachment = models.RPMSAttachment.objects.filter(attachment_id=attachment_id).first()
            attachment.teacher_comments.append(
                        {
                            'comment' : comment, 
                            'date' : (timezone.now()) , 
                            'role' : 'Evaluator', 
                            'name' : user.fullname,
                            'image' : user.profile.url if user.profile else ''
                        }
                    )
            attachment.save()
            return JsonResponse({
                'message' : 'Comment added successfully',
                }, status=200)
            
                
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


