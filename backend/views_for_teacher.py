
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








# ================================= Teacher Views =============================== #
@csrf_exempt
def login_teacher(request):
    """
    This function is used to login teacher.
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
            
            # TODO : CHECK IF THE USER IS TEACHER OR NOT
            
            
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
            'message' : 'Something went wrong',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def teacher_evaluation(request ):
    try:
        if request.method == 'GET': 
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            if user.role != 'Teacher':
                return JsonResponse({
                    'message' : 'User is not a teacher',
                    }, status=400)
            
            # Fetch filtered data
            ipcrf_forms = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1')  # Apply your filters here
            cot_forms = models.COTForm.objects.filter(employee_id=user.employee_id)  # Apply your filters here
            rpms_attachments = models.RPMSAttachment.objects.filter(employee_id=user.employee_id)  # Apply your filters here

            # Combine data
            combined_data = list(ipcrf_forms) + list(cot_forms) + list(rpms_attachments)

            # Sort combined data by 'created_at'
            sorted_data = sorted(combined_data, key=lambda x: x.created_at, reverse=True)
            
            
            return JsonResponse({
                'user' : user.get_information(),
                'forms' : [form.get_information() for form in sorted_data]
            },status=200)
        
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_forms(request ):
    try:
        if request.method == 'GET': 
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            if user.role != 'Teacher':
                return JsonResponse({
                    'message' : 'User is not a teacher',
                    }, status=400)
             
            return JsonResponse({
                'user' : user.get_information(),
                'position' : user.position,
            },status=200)
        
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_kba_breakdown(request ):
    try:
        if request.method == 'GET':
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            if user.role != 'Teacher':
                return JsonResponse({
                    'message' : 'User is not a teacher',
                    }, status=400)
             
            
            # 1. title and scores for KBA BREAKDOWN
            attachments = models.RPMSAttachment.objects.filter(employee_id=user.employee_id)
            
            # Sort attachments by 'streams_type'
            sorted_attachments = sorted(attachments, key=lambda x: x.streams_type)

            # Group by 'streams_type'
            grouped_attachments = {k: list(v) for k, v in groupby(sorted_attachments, key=lambda x: x.streams_type)}

            # Calculate all total scores each group
            total_scores = {}
            overall_scores = 0
            for group in grouped_attachments:
                score = sum([attachment.getTotalScores() for attachment in grouped_attachments[group]])
                total_scores[group] = score
                overall_scores += score
            total_scores['Overall'] = overall_scores
            
            
            return JsonResponse({
                'kba_breakdown' : total_scores,
            },status=200)
        
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_recommendations(request ):
    try:
        if request.method == 'GET':
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            if user.role != 'Teacher':
                return JsonResponse({
                    'message' : 'User is not a teacher',
                    }, status=400)
             
            # 2. rule based classifier for Promotion
            """
                ---------------RECOMMENDATION CHART PERCENTAGE-------------
                Dito sa chart na 'to magaappear yung percentage if promotion, termination, or retention

                *If promotion, their IPCRF score should range between 4.500 - 5.000 which is Outstanding

                *If retention, their IPCRF score should range between  3.500 – 4.499 (Very Satisfactory) and 2.500 – 3.499 (Satisfactory)

                *If termination, their IPCRF score should range between 1.500 – 2.499 (Unsatisfactory) and below 1.499 (Poor)

                {
                    '1' : {
                        'QUALITY' : '0',
                        'EFFICIENCY' : '0',
                        'TIMELINES' : '0',
                        'Total' : '0'
                    },
                    '2' : {
                        'QUALITY' : '0',
                        'EFFICIENCY' : '0',
                        'TIMELINES' : '0',
                        'Total' : '0'
                    }
                }
            
            
            """
            ipcrf_forms = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1')
            scores = [ form.getEvaluatorPart1Scores() for form in ipcrf_forms ]
            
            promotion_count = 0
            retention_count = 0
            termination_count = 0
            
            for score in scores:
                for _, value in score.items():
                    category = my_utils.classify_ipcrf_score(value['Average'])
                    if category == 'Promotion':
                        promotion_count += 1
                    elif category == 'Retention':
                        retention_count += 1
                    elif category == 'Termination':
                        termination_count += 1
            
            total = len(scores)
            promotion_percentage = promotion_count / total * 100 if total > 0 else 0
            retention_percentage = retention_count / total * 100 if total > 0 else 0
            termination_percentage = termination_count / total * 100 if total > 0 else 0
            recommendation = {
                'Promotion' : promotion_percentage,
                'Retention' : retention_percentage,
                'Termination' : termination_percentage
            }
            
            
            
            return JsonResponse({
                'recommendation' : recommendation,
            },status=200)
        
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    


@csrf_exempt
def teacher_performance(request ):
    try:
        if request.method == 'GET':
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            # TODO : CHECK IF THE USER IS TEACHER OR NOT
            # 3. date of submission and score Performance tru year
            """
            {
                "Year" : {
                    "Scores" : [],
                    "Total" : 0
                },
                "Year" : {
                    "Scores" : [],
                    "Total" : 0
                }
                
            }
            
            """
            # attachments = models.RPMSAttachment.objects.filter(employee_id=user.employee_id)
            attachments = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1').annotate(year=ExtractYear('created_at'))
            performances = {}
            for attachment in attachments:
                year = attachment.year
                if year not in performances:
                    performances[year] = {}
                    performances[year]['Scores'] = []
                performances[year]['Scores'].append( attachment.getEvaluatorPart1Scores())
            
            for year in performances:
                performances[year]['Total'] = sum(performances[year]['Scores'])
            
            # TODO : Add the current percentage added from the past year to the current year
            
            
            
            return JsonResponse({
                'performance' : performances,
            },status=200)
        
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    

@csrf_exempt
def teacher_swot(request ):
    try : 
        if request.method == 'GET':
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            if user.role != 'Teacher':
                return JsonResponse({
                    'message' : 'User is not a teacher',
                    }, status=400)
            
         
            # 4. generated text SWOT from COTForm 
            # cot_form = models.COTForm.objects.filter(employee_id=user.employee_id).first()
            generated_swot = {
                'Strengths': '',
                'Weaknesses': '',
                'Opportunities': '',
                'Threats': ''
            }
            # if cot_form:
            #     swot = cot_form.generatePromtTemplate()
            #     generated_swot["Strengths"] = my_utils.generate_text(swot["strengths"])
            #     generated_swot["Weaknesses"] = my_utils.generate_text(swot["weaknesses"])
            #     generated_swot["Opportunities"] = my_utils.generate_text(swot["opportunities"])
            #     generated_swot["Threats"] = my_utils.generate_text(swot["threats"])
            
            
            
            return JsonResponse({
                'swot' : generated_swot
            },status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_profile(request ):
    if request.method == 'GET':
        try:
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            return JsonResponse({
                'user' : user.get_information()
            },status=200)
        
        except Exception as e:
            return JsonResponse({
                'message' : f'Something went wrong : {e}',
                }, status=500)
    
        
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_upload_rpms(request):
    try:
        pass
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)





