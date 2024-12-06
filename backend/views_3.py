
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
            school_years = []
            for rmps_folder in rmps_folders:
                school_years.append(rmps_folder.rpms_folder_school_year)
            
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
            school_years = []
            for cot in cots:
                school_years.append(cot.school_year)
            
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

            ipcrfs = models.IPCRFForm.objects.filter(school_id=user.school_id).order_by('-created_at')
            school_years = []
            for ipcrf in ipcrfs:
                school_years.append(ipcrf.school_year)
            
            return JsonResponse({
                "school_years": school_years,
            }, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400) 






