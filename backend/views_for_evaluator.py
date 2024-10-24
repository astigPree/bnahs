
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










# ================================= Evaluator Views =============================== #
@csrf_exempt
def login_evaluator(request):
    """
    This function is used to login evaluator.
    """
    
    try:
        if request.method == 'POST':
            employee_id = request.POST.get('employee_id')
            password = request.POST.get('password')
            
            if not employee_id or not password:
                return JsonResponse({
                    'message' : 'Please provide employee_id and password',
                    }, status=400)
            
            user = models.People.objects.filter(employee_id=employee_id, password=password).first()
            if not user:
                return JsonResponse({
                    'message' : 'Invalid employee_id or password',
                    }, status=400)
                
            if user.role != 'Evaluator':
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
                'message' : 'Login successful'
                }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
        }, status=400)


@csrf_exempt
def evaluator_forms(request):
    
    return JsonResponse({
        'message' : 'Not yet implemented'
    }, status=400)
    
    
@csrf_exempt
def evaluator_records(request):
    
    return JsonResponse({
        'message' : 'Not yet implemented'
    }, status=400)
    
    
@csrf_exempt
def evaluator_summary(request):
    
    return JsonResponse({
        'message' : 'Not yet implemented'
    }, status=400)  


@csrf_exempt
def evaluator_profile(request):
    try:
        if request.method == 'GET':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            # TODO : IDENTIFY IF THE USER IS EVALUATOR OR NOT
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            return JsonResponse({
                'evaluator' : user.get_information(),
                }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
        }, status=400)


@csrf_exempt
def get_rating_sheet(request):
    try:
        if request.method == 'POST':
            evaluator = models.People.objects.filter(employee_id=request.user.username).first()
            if not evaluator:
                return JsonResponse({
                    'message' : 'Evaluator not found',
                    }, status=400)

            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'Teacher ID is required',
                    }, status=400)
            
            teacher = models.People.objects.filter(employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            cots = models.COTForm.objects.filter(evaluated_id=evaluator.employee_id , employee_id=teacher_id).first()
            
            return JsonResponse({
                'rating_sheet' : cots.get_information(),
            },status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
        }, status=400)

@csrf_exempt
def update_rating_sheet(request):
    try:
        if request.method == 'POST':
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            # TODO : WAIT FOR UPDATE IN IDENTIFICATION ID OF OBSERVER AND TEACHER
            # TODO : TELL THEM TO ADD IN THE HEADER 'Content-Type': 'application/json'
            """
            {
                "COT ID" : "COT ID",
                "COT Type" : "Proficient", ! Used to identify what rating type of form
                "Observer ID" : "Evaluator ID",
                "Observer Name" : "Evaluator Name",
                "Teacher Name" : "Evaluated Name",
                "Teacher ID" : "Evaluated ID",
                "Subject & Grade Level" : "Subject & Grade 7",
                "Date : "September 05, 2023", !Save date after submiting,
                "Quarter": "1st Quarter",
                "Questions" : {
                    "1" : {
                        "Objective" : "Applied knowledge of content within and across curriculum teaching areas. *",
                        "Selected" : "7" !Selected rate
                    },
                    "2" : {
                        "Objective" : "Applied knowledge of content within and across curriculum teaching areas. *",
                        "Selected" : "7" !Selected rate, kung "NO" means its "3"
                    }
                },
                "Comments" : ""
            }
            
            """
            content = json.loads(request.body)
            evaluator_id = content['Observer ID']
            evaluated_id = content['Teacher ID']
            questions = content['Questions']
            comments = content['Comments']
            cot_id = content['COT ID']
            
            for i in range(8):
                # used to check if the data still exist
                question_content = questions[f"{i+1}"]
                question = question_content['Objective']
                selected = question_content['Selected']
            
            search_evaluator = models.People.objects.filter(employee_id=evaluator_id, role='Evaluator').first()
            if not search_evaluator:
                return JsonResponse({
                    'message' : 'Evaluator not found',
                }, status=400)
            
            search_evaluated = models.People.objects.filter(employee_id=evaluated_id, role='Teacher').first()
            if not search_evaluated:
                return JsonResponse({
                    'message' : 'Evaluated not found',
                }, status=400)
            
            cot_form = models.COTForm.objects.filter(
                employee_id=evaluator_id,
                cot_form_id=cot_id
            ).first()
            
            if not cot_form:
                return JsonResponse({
                    'message' : 'COT form not found',
                }, status=400)
            
            my_utils.update_cot_form(cot_form=cot_form, comment=comments, questions=questions)
            
            return JsonResponse({
                'message' : 'Rating sheet updated successfully',
            }, status=200)
    
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_iprcf_form_for_evaluator_part_1_of_teacher(request):
    try:
        if request.method == 'POST':
            
            user = models.People.objects.filter(employee_id=request.user.username, role='Evaluator').first()
            if not user:
                return JsonResponse({
                   'message' : 'User not found',
                    }, status=400)
            
            # TODO : WAIT FOR UPDATE IN IDENTIFICATION ID OF OBSERVER AND TEACHER
            # TODO : TELL THEM TO ADD IN THE HEADER 'Content-Type': 'application/json'
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                   'message' : 'Teacher ID is required',
                    }, status=400)
            
            part_1 = models.IPCRFForm.objects.filter( employee_id=teacher_id , form_type="PART 1").first()
            
            if not part_1:
                return JsonResponse({
                    'message' : 'Invalid Teacher ID',
                    }, status=400)
            
            
            return JsonResponse({
                'evaluator content' : part_1.content_for_evaluator,
            }, status=200)
    
    except Exception as e:
        return JsonResponse({   
            'message' : f'Something went wrong : {e}',
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def check_teacher_ipcrf_form_part_1(request):
    try:
        
        if request.method == 'POST':
            
            user = models.People.objects.filter(employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            # TODO : WAIT FOR UPDATE IN IDENTIFICATION ID OF OBSERVER AND TEACHER
            # TODO : TELL THEM TO ADD IN THE HEADER 'Content-Type': 'application/json'
            
            connection_to_other = request.POST.get('ipcrf_id')
            if not connection_to_other:
                return JsonResponse({
                   'message' : 'Please provide IPCRF ID',
                    }, status=400)
            
            part_1 = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type="PART 1").first()
            
            if not part_1:
                return JsonResponse({
                    'message' : 'Invalid IPCRF ID',
                    }, status=400)
            
            teacher = models.People.objects.filter(employee_id=part_1.employee_id).first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)
            
            
            
            
            
            
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)




