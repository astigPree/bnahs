
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
def get_school_year_kra(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if not user:
                user = models.School.objects.filter(email_address=request.user.username).first()
                if not user:
                    return JsonResponse({
                        "message": "User not found",
                    }, status=404)

            rmps_folders = models.RPMSFolder.objects.filter(school_id=user.school_id).order_by('-created_at')
            school_years = {
                'proficient': [],
                'highly_proficient': []
            }
            for rmps_folder in rmps_folders:
                if rmps_folder.is_for_teacher_proficient:
                    if rmps_folder.rpms_folder_school_year not in school_years['proficient']:
                        school_years['proficient'].append(rmps_folder.rpms_folder_school_year)
                else:
                    if rmps_folder.rpms_folder_school_year not in school_years['highly_proficient']:
                        school_years['highly_proficient'].append(rmps_folder.rpms_folder_school_year)
            
            return JsonResponse({
                "school_years": school_years,
            }, status=200)
            
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)


@csrf_exempt
def get_school_year_cot(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(employee_id=request.user.username).first()

            if not user:
                user = models.School.objects.filter(email_address=request.user.username).first()
                if not user:
                    return JsonResponse({
                        "message": "User not found",
                    }, status=404)
                    
            cots = models.COTForm.objects.filter(school_id=user.school_id).order_by('-created_at')
            school_years = {
                'proficient': [],
                'highly_proficient': []
            }
            for cot in cots:
                if cot.is_for_teacher_proficient:
                    if cot.school_year not in school_years['proficient']:
                        school_years['proficient'].append(cot.school_year)
                else:
                    if cot.school_year not in school_years['highly_proficient']:
                        school_years['highly_proficient'].append(cot.school_year) 
            
            return JsonResponse({
                "school_years": school_years,
            }, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)



@csrf_exempt
def get_school_year_ipcrf(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                user = models.School.objects.filter(email_address=request.user.username).first()
                if not user:
                    return JsonResponse({
                        "message": "User not found",
                    }, status=404)

            ipcrfs = models.IPCRFForm.objects.filter(school_id=user.school_id , form_type="PART 1").order_by('-created_at')
            school_years = {
                'proficient': [],
                'highly_proficient': []
            }
            for ipcrf in ipcrfs:
                if ipcrf.is_for_teacher_proficient:
                    if ipcrf.school_year not in school_years['proficient']:
                        school_years['proficient'].append(ipcrf.school_year)
                else:
                    if ipcrf.school_year not in school_years['highly_proficient']:
                        school_years['highly_proficient'].append(ipcrf.school_year)
            
            return JsonResponse({
                "school_years": school_years,
            }, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400) 




@csrf_exempt
def get_school_year_ipcrf_all(request):
    try:
        if request.method == "GET": 

            ipcrfs = models.IPCRFForm.objects.filter(form_type="PART 1").order_by('-created_at')
            school_years = {
                'proficient': [],
                'highly_proficient': []
            }
            for ipcrf in ipcrfs:
                if ipcrf.is_for_teacher_proficient:
                    if ipcrf.school_year not in school_years['proficient']:
                        school_years['proficient'].append(ipcrf.school_year)
                else:
                    if ipcrf.school_year not in school_years['highly_proficient']:
                        school_years['highly_proficient'].append(ipcrf.school_year)
            
            return JsonResponse({
                "school_years": school_years,
            }, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400) 





@csrf_exempt
def react_post(request):
    try:
        if request.method == "POST":
            post_id = request.POST.get('post_id')
            if not post_id:
                return JsonResponse({"status": "error", "message": "Post ID is required"}, status=400)
            
            liked = request.POST.get('liked')
            if not liked:
                return JsonResponse({"status": "error", "message": "Liked is required"}, status=400)
            
            post = models.Post.objects.filter(post_id=post_id).first()
            if not post:
                return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
            
            if liked == "true":
                post.liked.append(request.user.username)
            else:
                post.liked.remove(request.user.username)
            
            post.save()
            
            return JsonResponse({"status": "success", "message": "Post updated successfully"}, status=200)
    
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
