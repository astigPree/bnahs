
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
def school_replied_to(request):
    try:
        if request.method == "POST":
            
            user = models.School.objects.filter(email_address=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
                
            comment_text = request.POST.get('comment')
            if not comment_text:
                return JsonResponse({
                    'message' : 'comment_text is required',
                    }, status=400)
            
            post_id = request.POST.get('post_id')
            if not post_id:
                return JsonResponse({
                    'message' : 'post_id is required',
                    }, status=400)
            
            
            post = models.Post.objects.filter(post_id=post_id).first()
            if not post:
                return JsonResponse({
                    'message' : 'Post not found',
                    }, status=400)
            
            reply_to = request.POST.get('replied_to')
            replied_comment = None
            if reply_to is not None and reply_to != '':
                replied_comment = models.Comment.objects.filter(post_id=post_id, comment_owner=reply_to).first()
            
            
            
            comment = models.Comment.objects.create(
                
                comment_owner=user.action_id,
            )
    
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

