
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
            remember_me = request.POST.get('remember_me', False)
            
            if not employee_id or not password:
                return JsonResponse({
                    'message' : 'Please provide employee_id and password',
                    }, status=400)
            
            user = models.People.objects.filter( is_accepted = True, employee_id=employee_id, password=password).first()
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
                    'message' : 'Invalid employee_id or password in authenticate ',
                    }, status=400)
            
            login(request, user_authenticated)
            if remember_me:
                request.session.set_expiry(1209600) # remember for 14 days
            else:
                request.session.set_expiry(0)
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
    
    try:
        
        if request.method == 'GET':
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username, role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            ipcrf_1_proficient = models.IPCRFForm.objects.filter(school_id=user.school_id, is_for_teacher_proficient=True).order_by('-created_at')
            ipcrf_1_highly_proficient = models.IPCRFForm.objects.filter(school_id=user.school_id, is_for_teacher_proficient=False).order_by('-created_at')
            
            number_of_conducted_ipcrf_1_proficient = ipcrf_1_proficient.count()
            number_of_conducted_ipcrf_1_highly_proficient = ipcrf_1_highly_proficient.count()
            number_of_evaluated_ipcrf_1_proficient = ipcrf_1_proficient.filter(is_checked=True).count()
            number_of_evaluated_ipcrf_1_highly_proficient = ipcrf_1_highly_proficient.filter(is_checked=True).count()
            
            # number_of_pending_ipcrf_1_proficient = number_of_conducted_ipcrf_1_proficient - number_of_evaluated_ipcrf_1_proficient
            # number_of_pending_ipcrf_1_highly_proficient = number_of_conducted_ipcrf_1_highly_proficient - number_of_evaluated_ipcrf_1_highly_proficient
            # response_rate_of_ipcrf_1_proficient = number_of_evaluated_ipcrf_1_proficient / number_of_conducted_ipcrf_1_proficient
            # response_rate_of_ipcrf_1_highly_proficient = number_of_evaluated_ipcrf_1_highly_proficient / number_of_conducted_ipcrf_1_highly_proficient
            
            # Calculate the number of pending IPCRF
            number_of_pending_ipcrf_1_proficient = number_of_conducted_ipcrf_1_proficient - number_of_evaluated_ipcrf_1_proficient
            number_of_pending_ipcrf_1_highly_proficient = number_of_conducted_ipcrf_1_highly_proficient - number_of_evaluated_ipcrf_1_highly_proficient

            # Handle division by zero
            if number_of_conducted_ipcrf_1_proficient != 0:
                response_rate_of_ipcrf_1_proficient = (number_of_evaluated_ipcrf_1_proficient / number_of_conducted_ipcrf_1_proficient) * 100
            else:
                response_rate_of_ipcrf_1_proficient = 0  # or handle this case as needed

            if number_of_conducted_ipcrf_1_highly_proficient != 0:
                response_rate_of_ipcrf_1_highly_proficient = (number_of_evaluated_ipcrf_1_highly_proficient / number_of_conducted_ipcrf_1_highly_proficient) * 100
            else:
                response_rate_of_ipcrf_1_highly_proficient = 0  # or handle this case as needed

            
            
            cot_proficient = models.COTForm.objects.filter(school_id=user.school_id, is_for_teacher_proficient=True).order_by('-created_at')
            cot_highly_proficient = models.COTForm.objects.filter(school_id=user.school_id, is_for_teacher_proficient=False).order_by('-created_at')
            
            number_of_conducted_cot_proficient = cot_proficient.count()
            number_of_conducted_cot_highly_proficient = cot_highly_proficient.count()
            number_of_evaluated_cot_proficient = cot_proficient.filter(is_checked=True).count()
            number_of_evaluated_cot_highly_proficient = cot_highly_proficient.filter(is_checked=True).count()
            # number_of_pending_cot_proficient = number_of_conducted_cot_proficient - number_of_evaluated_cot_proficient
            # number_of_pending_cot_highly_proficient = number_of_conducted_cot_highly_proficient - number_of_evaluated_cot_highly_proficient
            # response_rate_of_cot_proficient = number_of_evaluated_cot_proficient / number_of_conducted_cot_proficient
            # response_rate_of_cot_highly_proficient = number_of_evaluated_cot_highly_proficient / number_of_conducted_cot_highly_proficient
            
            # Calculate the number of pending COT
            number_of_pending_cot_proficient = number_of_conducted_cot_proficient - number_of_evaluated_cot_proficient
            number_of_pending_cot_highly_proficient = number_of_conducted_cot_highly_proficient - number_of_evaluated_cot_highly_proficient

            # Handle division by zero for response rates
            if number_of_conducted_cot_proficient != 0:
                response_rate_of_cot_proficient = (number_of_evaluated_cot_proficient / number_of_conducted_cot_proficient) * 100
            else:
                response_rate_of_cot_proficient = 0  # or handle this case as needed

            if number_of_conducted_cot_highly_proficient != 0:
                response_rate_of_cot_highly_proficient = (number_of_evaluated_cot_highly_proficient / number_of_conducted_cot_highly_proficient) * 100
            else:
                response_rate_of_cot_highly_proficient = 0  # or handle this case as needed

            
            
            rpms_proficient = models.RPMSAttachment.objects.filter(school_id=user.school_id, is_submitted=True, is_for_teacher_proficient=True).order_by('-created_at')
            rpms_highly_proficient = models.RPMSAttachment.objects.filter(school_id=user.school_id, is_submitted=True, is_for_teacher_proficient=False).order_by('-created_at')
            
            number_of_conducted_rpms_proficient = rpms_proficient.count()
            number_of_conducted_rpms_highly_proficient = rpms_highly_proficient.count()
            number_of_evaluated_rpms_proficient = rpms_proficient.filter(is_checked=True).count()
            number_of_evaluated_rpms_highly_proficient = rpms_highly_proficient.filter(is_checked=True).count()
            # number_of_pending_rpms_proficient = number_of_conducted_rpms_proficient - number_of_evaluated_rpms_proficient
            # number_of_pending_rpms_highly_proficient = number_of_conducted_rpms_highly_proficient - number_of_evaluated_rpms_highly_proficient
            # response_rate_of_rpms_proficient = number_of_evaluated_rpms_proficient / number_of_conducted_rpms_proficient
            # response_rate_of_rpms_highly_proficient = number_of_evaluated_rpms_highly_proficient / number_of_conducted_rpms_highly_proficient
            
            # Calculate the number of pending RPMS
            number_of_pending_rpms_proficient = number_of_conducted_rpms_proficient - number_of_evaluated_rpms_proficient
            number_of_pending_rpms_highly_proficient = number_of_conducted_rpms_highly_proficient - number_of_evaluated_rpms_highly_proficient

            # Handle division by zero for response rates
            if number_of_conducted_rpms_proficient != 0:
                response_rate_of_rpms_proficient = (number_of_evaluated_rpms_proficient / number_of_conducted_rpms_proficient) * 100
            else:
                response_rate_of_rpms_proficient = 0  # or handle this case as needed

            if number_of_conducted_rpms_highly_proficient != 0:
                response_rate_of_rpms_highly_proficient = (number_of_evaluated_rpms_highly_proficient / number_of_conducted_rpms_highly_proficient) * 100
            else:
                response_rate_of_rpms_highly_proficient = 0  # or handle this case as needed

            
            return JsonResponse({
                'number_of_conducted_ipcrf_1_proficient' : number_of_conducted_ipcrf_1_proficient,
                'number_of_conducted_ipcrf_1_highly_proficient' : number_of_conducted_ipcrf_1_highly_proficient,
                'number_of_evaluated_ipcrf_1_proficient' : number_of_evaluated_ipcrf_1_proficient,
                'number_of_evaluated_ipcrf_1_highly_proficient' : number_of_evaluated_ipcrf_1_highly_proficient,
                'number_of_pending_ipcrf_1_proficient' : number_of_pending_ipcrf_1_proficient,
                'number_of_pending_ipcrf_1_highly_proficient' : number_of_pending_ipcrf_1_highly_proficient,
                'number_of_conducted_cot_proficient' : number_of_conducted_cot_proficient,
                'number_of_conducted_cot_highly_proficient' : number_of_conducted_cot_highly_proficient,
                'number_of_evaluated_cot_proficient' : number_of_evaluated_cot_proficient,
                'number_of_evaluated_cot_highly_proficient' : number_of_evaluated_cot_highly_proficient,
                'number_of_pending_cot_proficient' : number_of_pending_cot_proficient,
                'number_of_pending_cot_highly_proficient' : number_of_pending_cot_highly_proficient,
                'number_of_conducted_rpms_proficient' : number_of_conducted_rpms_proficient,
                'number_of_conducted_rpms_highly_proficient' : number_of_conducted_rpms_highly_proficient,
                'number_of_evaluated_rpms_proficient' : number_of_evaluated_rpms_proficient,
                'number_of_evaluated_rpms_highly_proficient' : number_of_evaluated_rpms_highly_proficient,
                'number_of_pending_rpms_proficient' : number_of_pending_rpms_proficient,
                'number_of_pending_rpms_highly_proficient' : number_of_pending_rpms_highly_proficient,
                'response_rate_of_ipcrf_1_proficient' : response_rate_of_ipcrf_1_proficient,
                'response_rate_of_ipcrf_1_highly_proficient' : response_rate_of_ipcrf_1_highly_proficient,
                'response_rate_of_cot_proficient' : response_rate_of_cot_proficient,
                'response_rate_of_cot_highly_proficient' : response_rate_of_cot_highly_proficient,
                'response_rate_of_rpms_proficient' : response_rate_of_rpms_proficient,
                'response_rate_of_rpms_highly_proficient' : response_rate_of_rpms_highly_proficient
                }, status=200)
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
    }, status=400)
    
    
@csrf_exempt
def evaluator_records(request):
    
    try:
        
        if request.method == 'POST':
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username).first()
            # TODO : IDENTIFY IF THE USER IS EVALUATOR OR NOT
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            school_year = request.POST.get('school_year')
            school_year = school_year if school_year else 'all'
            
            position = request.POST.get('position')
            position = position if position else 'all'
            
            
            school = models.School.objects.filter(school_id=user.school_id).first()
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                    }, status=400)
                
            teachers = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role='Teacher').order_by('-created_at')
            
            if not teachers:
                return JsonResponse({
                    'message' : 'No teachers found',
                    }, status=400)
            
            cots = {}
            ipcrfs = {}
            rpms = {}
            """
                {
                    "Teacher" : {},
                }
            """
            
            for teacher in teachers:
                # ADD CHECK IF in filter IT EVALUATED
                cot = models.COTForm.objects.filter(evaluated_id=teacher.employee_id ).order_by('-created_at').first()
                ipcrf = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id , form_type="PART 1" ).order_by('-created_at').first()
                rpm = models.RPMSAttachment.objects.filter(employee_id=teacher.employee_id ).order_by('-created_at').first()
                
                cots[teacher.employee_id] = {
                    'teacher' : teacher.get_information(),
                    'cot' : cot.get_information() if cot else None,
                }
                
                ipcrfs[teacher.employee_id] = {
                    'teacher' : teacher.get_information(),
                    'ipcrf' : ipcrf.get_information() if ipcrf else None,
                }
                
                rpms[teacher.employee_id] = {
                    'teacher' : teacher.get_information(),
                    'rpm' : rpm.get_information() if rpm else None,
                }
    
            return JsonResponse({ 
                'cots' : cots,
                'ipcrfs' : ipcrfs,
                'rpms' : rpms,  
            }, status=200)
            
        
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
    }, status=400)



@csrf_exempt
def evaluator_get_annual_ratings(request):
    try:
        if request.method == 'GET':
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username).first()
            # TODO : IDENTIFY IF THE USER IS EVALUATOR OR NOT
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            teachers_ratings = {
                "all" : {
                    "names" : [],
                    "ratings" : [],
                },
                "proficient" : {
                    "names" : [],
                    "ratings" : [],
                },
                "highly_proficient" : {
                    "names" : [],
                    "ratings" : [],
                },
            }
            
            
            teachers = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role='Teacher').order_by('-created_at')
            if not teachers:
                return JsonResponse(teachers_ratings, status=400)
            
            for teacher in teachers:
                ipcrf_1 = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id, form_type='PART 1').order_by('-created_at').first() 
                if ipcrf_1:
                    if my_utils.is_proficient_faculty(teacher):
                        teachers_ratings["proficient"]["names"].append(teacher.first_name)
                        teachers_ratings["proficient"]["ratings"].append(ipcrf_1.evaluator_rating)
                    else:
                        teachers_ratings["highly_proficient"]["names"].append(teacher.first_name)
                        teachers_ratings["highly_proficient"]["ratings"].append(ipcrf_1.evaluator_rating)
                    
                    teachers_ratings["all"]["names"].append(teacher.first_name)
                    teachers_ratings["all"]["ratings"].append(ipcrf_1.evaluator_rating)
            
            return JsonResponse(teachers_ratings, status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
    }, status=400)



@csrf_exempt
def evaluator_get_all_teacher_tenure(request):
    try:
        
        if request.method == 'GET':
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username, role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            data = {
                "all" : {
                    '0-3 years': 0,
                    '3-5 years': 0,
                    '5+ years': 0
                },
                "proficient" : {
                    '0-3 years': 0,
                    '3-5 years': 0,
                    '5+ years': 0
                },
                "highly_proficient" : {
                    '0-3 years': 0,
                    '3-5 years': 0,
                    '5+ years': 0
                }
            }

            people = People.objects.filter(role='Teacher', school_id=user.school_id)
            total_count = people.count()
            
            if total_count == 0:
                return JsonResponse(data, status=200)

            # Initialize counters
            proficient_count = 0
            highly_proficient_count = 0
            for person in people:
                tenure_category = person.get_tenure_category()
                if tenure_category in data['all']:
                    data['all'][tenure_category] += 1
                if my_utils.is_proficient_faculty(person):
                    data['proficient'][tenure_category] += 1
                    proficient_count += 1
                else:
                    data['highly_proficient'][tenure_category] += 1
                    highly_proficient_count += 1
            
            if proficient_count == 0:
                proficient_count = 1
            if highly_proficient_count == 0:
                highly_proficient_count = 1
            
            # Calculate percentages
            data['all'] = {
                category: (count / total_count) * 100 for category, count in data['all'].items()
            }
            data['proficient'] = {
                category: (count / proficient_count) * 100 for category, count in data['proficient'].items()
            }
            data['highly_proficient'] = {
                category: (count / highly_proficient_count) * 100 for category, count in data['highly_proficient'].items()
            }
            
            return JsonResponse(data, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def evaluator_get_teacher_recommendations(request):
    try:
        if request.method == 'GET':
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username).first()
            # TODO : IDENTIFY IF THE USER IS EVALUATOR OR NOT
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            data = {
                "proficient" : {
                    "number_of_promotion" : 0,
                    "number_of_termination" : 0,
                    "number_of_retention" : 0 ,
                    "number_of_promotion_by_percentage" : 0.0,
                    "number_of_termination_by_percentage" : 0.0,
                    "number_of_retention_by_percentage" : 0.0
                },
                "highly_proficient" : {
                    "number_of_promotion" : 0,
                    "number_of_termination" : 0,
                    "number_of_retention" : 0 ,
                    "number_of_promotion_by_percentage" : 0.0,
                    "number_of_termination_by_percentage" : 0.0,
                    "number_of_retention_by_percentage" : 0.0
                },
                "all" : {
                    "number_of_promotion" :0,
                    "number_of_termination" : 0,
                    "number_of_retention" : 0,
                    "number_of_promotion_by_percentage" : 0.0,
                    "number_of_termination_by_percentage" : 0.0,
                    "number_of_retention_by_percentage" : 0.0
                }
            }
            
            
            
            # FOR ALL TEACHER
            teachers = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role='Teacher')
            proficient_count = 0
            highly_proficient_count = 0
            for teacher in teachers:
                result = my_utils.get_recommendation_result(employee_id=teacher.employee_id)
                if result == 'Promotion':
                    if my_utils.is_proficient_faculty(people=teacher):
                        data["proficient"]["number_of_promotion"] += 1
                        proficient_count += 1
                    else:
                        data["highly_proficient"]["number_of_promotion"] += 1
                        highly_proficient_count += 1
                    data["all"]["number_of_promotion"] += 1
                elif result == 'Termination':
                    if my_utils.is_proficient_faculty(people=teacher):
                        data["proficient"]["number_of_termination"] += 1
                        proficient_count += 1
                    else:
                        data["highly_proficient"]["number_of_termination"] += 1
                        highly_proficient_count += 1
                    data["all"]["number_of_termination"] += 1
                elif result == 'Retention':
                    if my_utils.is_proficient_faculty(people=teacher):
                        data["proficient"]["number_of_retention"] += 1
                        proficient_count += 1
                    else:
                        data["highly_proficient"]["number_of_retention"] += 1
                        highly_proficient_count += 1
                    data["all"]["number_of_retention"] += 1
            
            data["all"]["number_of_promotion_by_percentage"] = (data["all"]["number_of_promotion"] / teachers.count()) * 100 if teachers.count() > 0 else 0
            data["all"]["number_of_termination_by_percentage"] = (data["all"]["number_of_termination"] / teachers.count()) * 100 if teachers.count() > 0 else 0
            data["all"]["number_of_retention_by_percentage"] = (data["all"]["number_of_retention"] / teachers.count()) * 100 if teachers.count() > 0 else 0
            
            data["proficient"]["number_of_promotion_by_percentage"] = (data["proficient"]["number_of_promotion"] / proficient_count) * 100 if proficient_count > 0 else 0
            data["proficient"]["number_of_termination_by_percentage"] = (data["proficient"]["number_of_termination"] / proficient_count) * 100 if proficient_count > 0 else 0
            data["proficient"]["number_of_retention_by_percentage"] = (data["proficient"]["number_of_retention"] / proficient_count) * 100 if proficient_count > 0 else 0
            
            data["highly_proficient"]["number_of_promotion_by_percentage"] = (data["highly_proficient"]["number_of_promotion"] / highly_proficient_count) * 100 if highly_proficient_count > 0 else 0
            data["highly_proficient"]["number_of_termination_by_percentage"] = (data["highly_proficient"]["number_of_termination"] / highly_proficient_count) * 100 if highly_proficient_count > 0 else 0
            data["highly_proficient"]["number_of_retention_by_percentage"] = (data["highly_proficient"]["number_of_retention"] / highly_proficient_count) * 100 if highly_proficient_count > 0 else 0
            
            return JsonResponse(data, status=200)
            
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def evaluator_get_performance_true_year(request):
    try:
        if request.method == 'GET':
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username).first()
            # TODO : IDENTIFY IF THE USER IS EVALUATOR OR NOT
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            teachers = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role='Teacher') 
            if not teachers:
                return JsonResponse({
                    'message' : 'Teachers not found',
                    }, status=400)
                
            
            teacher_performance = {
                "all" : [],
                "proficient" : [],
                "highly_proficient" : []
            }
            for teacher in teachers:
                result = my_utils.get_performance_by_years(employee_id=teacher.employee_id)
                temp = {
                    "data" : result,
                    "name" : teacher.first_name
                }
                teacher_performance["all"].append(temp)
                if my_utils.is_proficient_faculty(people=teacher):
                    teacher_performance["proficient"].append(temp)
                else:
                    teacher_performance["highly_proficient"].append(temp)
            
            return JsonResponse(teacher_performance, status=200)
             
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def evaluator_profile(request):
    try:
        if request.method == 'GET':
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username).first()
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
            evaluator = models.People.objects.filter(is_accepted = True, employee_id=request.user.username).first()
            if not evaluator:
                return JsonResponse({
                    'message' : 'Evaluator not found',
                    }, status=400)

            teacher_id = request.POST.get('teacher_id')
            quarter = request.POST.get('quarter')
            cot_id = request.POST.get('cot_id')
            
            if not cot_id:
                return JsonResponse({
                    'message' : 'cot_id is required',
                    }, status=400) 
            
            if not teacher_id:
                return JsonResponse({
                    'message' : 'Teacher ID is required',
                    }, status=400)
            
            if not quarter:
                return JsonResponse({
                    'message' : 'Quarter is required',
                    }, status=400)
            
            teacher = models.People.objects.filter(is_accepted = True, school_id=evaluator.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            cots = models.COTForm.objects.filter(school_id=evaluator.school_id, quarter=quarter , evaluated_id=teacher_id).order_by('-created_at').first()
            
            return JsonResponse({
                'cot' : cots.get_information() if cots else {},
                'teacher' : teacher.get_information(),
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
            
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            # TODO : WAIT FOR UPDATE IN IDENTIFICATION ID OF OBSERVER AND Teacher
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
            
            
            cot_id = request.POST.get('cot_form_id')
            if not cot_id:
                return JsonResponse({
                    'message' : 'cot_form_id is required',
                    }, status=400)
            
            subject = request.POST.get('subject')
            if not subject:
                return JsonResponse({
                    'message' : 'subject is required',
                    'subject' : subject
                    }, status=400)
            
             
            content = json.loads(request.POST.get('content'))
            content['Observer ID'] = user.employee_id
            evaluator_id = content['Observer ID']
            evaluated_id = content['Teacher ID']
            questions = content['Questions']
            comments = content['Comments'] 
            quarter = content['Quarter']
                
            for i in range(8):
                # used to check if the data still exist
                question_content = questions[f"{i+1}"]
                question = question_content['Objective']
                selected = question_content['Selected']
            
            search_evaluator = models.People.objects.filter(is_accepted = True, employee_id=evaluator_id, role='Evaluator').first()
            if not search_evaluator:
                return JsonResponse({
                    'message' : 'Evaluator not found',
                }, status=400)
            
            search_evaluated = models.People.objects.filter(is_accepted = True, employee_id=evaluated_id, role='Teacher').first()
            if not search_evaluated:
                return JsonResponse({
                    'message' : 'Evaluated not found',
                }, status=400)
            
            cot_form = models.COTForm.objects.filter(
                evaluated_id=evaluated_id,
                cot_form_id=cot_id,
                quarter=quarter,
                school_id=search_evaluated.school_id
            ).order_by('-created_at').first()
            
            if not cot_form:
                return JsonResponse({
                    'message' : 'COT form not found',
                }, status=400)
            
            
            cot_form.subject = subject
            cot_form.employee_id = user.employee_id
            cot_form.check_date = timezone.now()
            my_utils.update_cot_form(cot_form=cot_form, comment=comments, questions=questions , content=content)
            
            
            evaluation = ""
            if not search_evaluated.is_evaluated:
                evaluation = search_evaluated.update_is_evaluted()
            
             
            return JsonResponse({
                'message' : 'Rating sheet updated successfully',
                'evaluation' : evaluation,
            }, status=200)
    
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)





@csrf_exempt
def get_iprcf_form_for_evaluator_part_1_of_all_teacher(request):
    try:
        
        if request.method == "GET":
                        
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username, role='Evaluator').first()
            if not user:
                return JsonResponse({
                   'message' : 'User not found',
                    }, status=400)
            
            
            ipcrf_forms_for_proficient = models.IPCRFForm.objects.filter( school_id=user.school_id , is_for_teacher_proficient=True , form_type="PART 1").order_by('-created_at')
            
            proficient_employee_ids = []
            ipcrf_forms_data_proficient = []
            for ipcrf_form in ipcrf_forms_for_proficient:
                if ipcrf_form.employee_id not in proficient_employee_ids:
                    teacher = models.People.objects.filter(is_accepted = True, employee_id=ipcrf_form.employee_id, role='Teacher').first()
                    if teacher:
                        proficient_employee_ids.append(ipcrf_form.employee_id)
                        ipcrf_forms_data_proficient.append({
                            'teacher' : teacher.get_information(),
                            'ipcrf_form' : ipcrf_form.get_information(),
                        })
            
            ipcrf_forms_for_highly_proficient = models.IPCRFForm.objects.filter( school_id=user.school_id , is_for_teacher_proficient=False , form_type="PART 1").order_by('-created_at')
            highly_proficient_employee_ids = []
            ipcrf_forms_data_highly_proficient = []
            for ipcrf_form in ipcrf_forms_for_highly_proficient:
                if ipcrf_form.employee_id not in highly_proficient_employee_ids:
                    teacher = models.People.objects.filter(is_accepted = True, employee_id=ipcrf_form.employee_id, role='Teacher').first()
                    if teacher:
                        highly_proficient_employee_ids.append(ipcrf_form.employee_id)
                        ipcrf_forms_data_highly_proficient.append({
                            'teacher' : teacher.get_information(),
                            'ipcrf_form' : ipcrf_form.get_information(), 
                        })

            return JsonResponse({
                'message' : 'IPRCF forms for evaluator',
                'ipcrf_forms_data_proficient' : ipcrf_forms_data_proficient,
                'ipcrf_forms_data_highly_proficient' : ipcrf_forms_data_highly_proficient,
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
            
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username, role='Evaluator').first()
            if not user:
                return JsonResponse({
                   'message' : 'User not found',
                    }, status=400)
            
            # TODO : WAIT FOR UPDATE IN IDENTIFICATION ID OF OBSERVER AND Teacher 
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                   'message' : 'Teacher ID is required',
                    }, status=400)
            
            part_1 = models.IPCRFForm.objects.filter( employee_id=teacher_id , school_id=user.school_id , form_type="PART 1").order_by('-created_at').first()
            
            if not part_1:
                return JsonResponse({
                    'message' : 'Invalid Teacher ID',
                    }, status=400)
            
            
            return JsonResponse(part_1.get_information(), status=200)
    
    except Exception as e:
        return JsonResponse({   
            'message' : f'Something went wrong : {e}',
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def check_teacher_ipcrf_form_part_1_by_evaluator(request):
    try:
        
        if request.method == 'POST':
            
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            # TODO : WAIT FOR UPDATE IN IDENTIFICATION ID OF OBSERVER AND Teacher
            """
                {
                    'ipcrf_id' : 'ipcrf_id',
                    'content' : {...} !Content/Checked of IPCRF form from teacher
                    'total_score' : 0.328,
                    'plus_factor' : numbers,
                    'average_score' numbers,
                }
            """
            
            connection_to_other = request.POST.get('ipcrf_id')
            content : dict[str , dict] = json.loads(request.POST.get('content', None))
            rating = request.POST.get('total_score', None)
            plus_factor = request.POST.get('plus_factor', None)
            average_score = request.POST.get('average_score', None)
            
            if not rating:
                return JsonResponse({
                    'message' : 'Rating not found',
                }, status=400)
            if not connection_to_other:
                return JsonResponse({
                    'message' : 'Connection to other not found',
                }, status=400)
            if not plus_factor:
                return JsonResponse({
                    'message' : 'Plus Factor score not found',
                }, status=400)
            if not average_score:
                return JsonResponse({
                    'message' : 'Average score not found',
                }, status=400)
            if not content:
                return JsonResponse({
                    'message' : 'Content not found',
                }, status=400)
             
            
            part_1 = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type="PART 1").order_by('-created_at').first()
            
            if not part_1:
                return JsonResponse({
                    'message' : 'Invalid IPCRF ID',
                    }, status=400)
            
            teacher = models.People.objects.filter(is_accepted = True, employee_id=part_1.employee_id, role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)
            
            school = models.School.objects.filter(school_id=teacher.school_id).first()
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                    }, status=400)
            
            part_1.check_date = timezone.now()
            part_1.evaluator_id = user.employee_id
            part_1.evaluator_rating = rating
            part_1.evaluator_plus_factor = plus_factor
            part_1.evaluator_average_score = average_score
            my_utils.update_ipcrf_form_part_1_by_evaluator(
                 ipcrf_form=part_1, content=content    
            )
             
            evaluation = ""
            if not teacher.is_evaluated:
                evaluation = teacher.update_is_evaluted()
            
            
            return JsonResponse({
                'message' : 'Form updated successfully',
                'evaluation' : evaluation
            },status=200)
            
            
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_all_teacher_in_school(request):
    try:
        if request.method == 'GET':
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username).first() 
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
  
            teachers = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role='Teacher').order_by('-created_at')
            
            teachers_data = []
            for teacher in teachers:
                data = teacher.get_information() 
                
                one_year_ago = timezone.now() - timedelta(days=365)
                ipcrf_forms_last_year = models.IPCRFForm.objects.filter(created_at__gte=one_year_ago , employee_id=teacher.employee_id).order_by('-created_at')
                data['ipcrf_quarter'] = [  ]
                if ipcrf_forms_last_year: 
                    school_year = ""
                    quarter = 1
                    for form in ipcrf_forms_last_year:
                        if len(school_year) == 0:
                            school_year = form.school_year
                            
                        if school_year == form.school_year:
                            data['ipcrf_quarter'].append({f"Quarter {quarter}" : form.get_information() })
                            quarter += 1 
                
                cot = models.COTForm.objects.filter(created_at__gte=one_year_ago , evaluated_id=teacher.employee_id).order_by('-created_at').first()
                data['cot_quarter'] = []
                if cot:
                    data['cot_quarter'].append({
                        "Quarter 1" : cot.get_information()
                    })
                
                rpms = models.RPMSAttachment.objects.filter(created_at__gte=one_year_ago , employee_id=teacher.employee_id).order_by('-created_at')
                data['rpms_quarter'] = []
                if rpms:
                    data['rpms_quarter'].append({
                        "Quarter 1" : [ rpm.get_information() for rpm in rpms]
                    })
                teachers_data.append(data)
                
            return JsonResponse({
                'teachers' : teachers_data ,
            }, status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 
    
    
    
@csrf_exempt
def get_rating_sheet_for_all_teacher(request):
    try:
        if request.method == 'GET':
            
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username, role='Evaluator').first()
            if not user:
                return JsonResponse({
                   'message' : 'User not found',
                    }, status=400)
            
            quarters = {
                "Quarter 1" : [],
                "Quarter 2" : [],
                "Quarter 3" : [],
                "Quarter 4" : [],
            }
            
            for quarter in quarters:
                cots = models.COTForm.objects.filter(quarter=quarter , school_id=user.school_id).order_by('-created_at')
                for cot in cots:
                    teacher = models.People.objects.filter(school_id=user.school_id, employee_id=cot.evaluated_id).first()
                    if teacher:
                        quarters[quarter].append({
                            'teacher' : teacher.get_information(),
                            'cot' : cot.get_information()
                        })

            return JsonResponse(quarters, status=200)
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    


@csrf_exempt
def evaluator_check_rpms_attachment(request):
    try:
        
        if request.method == 'POST':
            
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            # TODO : WAIT FOR UPDATE IN IDENTIFICATION ID OF OBSERVER AND Teacher
            """
                {
                    'rpms_id' : 'rpms_id',
                    'content' : {...} !Content/Checked of RPMS form from teacher
                }
            """
            
            rpms_id = request.POST.get('rpms_id')
            content : dict[str , dict] = json.loads(request.POST.get('content', None))
            comment = request.POST.get('comment', None)
            
            if not rpms_id:
                return JsonResponse({
                   'message' : 'Please provide rpms_id',
                    }, status=400)
            
            if not content:
                return JsonResponse({
                    'message' : 'content is required',
                    }, status=400)
            
            if not comment:
                return JsonResponse({
                    'message' : 'comment is required',
                    }, status=400)
            
            rpms = models.RPMSAttachment.objects.filter(attachment_id=rpms_id).order_by('-created_at').first()
            if not rpms:
                return JsonResponse({
                    'message' : 'Invalid RPMS ID',
                    }, status=400)
            
            
            rpms.evaluator_id = user.employee_id
            my_utils.update_rpms_attachment(rpms_attachment=rpms, content=content , comment=comment)
            
            teacher = models.People.objects.filter(is_accepted = True, employee_id=rpms.employee_id, role='Teacher').first()
            evaluation = ""
            if not teacher.is_evaluated:
                evaluation = teacher.update_is_evaluted()
            
            return JsonResponse({
                'message' : 'Form updated successfully',
                'evaluation' : evaluation
            },status=200)
            
        
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def evaluator_get_list_of_rpms_takers(request):
    try:
        
        if request.method == 'GET':
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
                
            # Get the latest folder
            folders = models.RPMSFolder.objects.filter(school_id=user.school_id).order_by('-created_at')
            if not folders:
                return JsonResponse({
                    'message' : 'No folders found',
                    }, status=400)

            teachers = models.People.objects.filter(school_id=user.school_id, role='Teacher').order_by('-created_at')
            
            
            teachers_rpms = []
            """
            [
                {
                    'teacher' : {...},
                    'rater' : '',
                    'status' : 'Pending'
                }
            ]
            
            STATUS: 
            “Pending” (Action - Review)
            Kapag hindi pa tapos gradan ni Evaluator lahat ng attachments.

            “Submitted” (Action - Reviewed)
            Once na tapos nang masagutan ni evaluator lahat ng pinasa ni teacher. And once na nireturn na rin ni Evaluator yung scores.

            “No Attachments” (Action - Blank)
            Kapag wala pa ni isang attachment na pinasa si teacher
            """
            
            for teacher in teachers:
                teacher_data = {
                    'teacher' : teacher.get_information(),
                    'rater' : None,
                    'status' : 'Pending',
                    'number_of_submitted' : 0,
                    'number_of_checked' : 0
                }
                # TODO : FIX IT SOON
                contain_atleast_one_rpms = False
                
                for folder in folders:
                    classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=folder.rpms_folder_id).order_by('-created_at')
                    for classwork in classworks:
                        rpms_attachments = models.RPMSAttachment.objects.filter(
                            class_work_id=classwork.class_work_id, 
                            employee_id=teacher.employee_id).order_by('-created_at')
                        
                        if rpms_attachments:
                            contain_atleast_one_rpms = True
                            teacher_data['number_of_submitted'] += 1
                            for rpms_attachment in rpms_attachments:
                                if rpms_attachment.is_checked:
                                    teacher_data['number_of_checked'] += 1
                                    teacher_data['status'] = 'Submitted'
                                    teacher_data['rater'] = models.People.objects.filter(employee=rpms_attachment.evaluator_id).first().get_information()
                                
                    if not contain_atleast_one_rpms:
                        teacher_data['status'] = 'No Attachments'
                
                teachers_rpms.append(teacher_data)
            
            return JsonResponse({ 'teachers' : teachers_rpms}, status=200)
                
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    

@csrf_exempt
def evaluator_get_rpms_folders(request):
    # Used to view all the folder
    try:
        
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first() 
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            folder_type = request.POST.get('folder_type')
            
            if folder_type not in ['proficient', 'highly_proficient']:
                return JsonResponse({
                    'message' : 'Invalid folder_type must contain proficient or highly_proficient',
                }, status=400)
            
            
            
            rpms_folders = models.RPMSFolder.objects.filter(
                school_id=user.school_id,
                is_for_teacher_proficient= True if folder_type == 'proficient' else False
                ).order_by('-created_at')
            
            return JsonResponse({
                'rpms_folders' : [rpms_folder.get_rpms_folder_information() for rpms_folder in rpms_folders],
            },status=200)
    
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
    },status=400)



@csrf_exempt
def evaluator_get_rpms_work(request):
    try:
        
        if request.method == 'POST':
            
            user = models.People.objects.filter(employee_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            class_work_id = request.POST.get('class_work_id')
            if not class_work_id:
                return JsonResponse({
                    'message' : 'class_work_id not found',
                }, status=400)
                
            classwork = models.RPMSClassWork.objects.filter(class_work_id=class_work_id).first()
            if not classwork:
                return JsonResponse({
                    'message' : 'Class Work not found',
                }, status=400)
            
            
            return JsonResponse({
                    'classwork' : classwork.get_rpms_classwork_information(),
                },status=200)
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
        },status=400)

    return JsonResponse({
        'message' : 'Invalid Request'
    },status=400)

 

@csrf_exempt
def evaluator_get_rpms_folder(request):
    try:
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            rpms_folder_id = request.POST.get('rpms_folder_id')
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'rpms_folder_id not found',
                }, status=400)
            
            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at').first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS Folder not found',
                }, status=400)
                
            classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at')
            
            return JsonResponse({
                'rpms_folder' : rpms_folder.get_rpms_folder_information(),
                'rpms_classworks' : [work.get_rpms_classwork_information() for work in classworks]
            },status=200)
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
    },status=400)

 

@csrf_exempt
def evaluator_get_rpms_work_attachments(request):
    try:
        
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            class_work_id = request.POST.get('class_work_id')
            teacher_id = request.POST.get('teacher_id')
            
            if not class_work_id:
                return JsonResponse({
                    'message' : 'class_work_id not found',
                },status=400)
            
            
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id not found',
                },status=400)
            
            teacher = models.People.objects.filter(employee_id=teacher_id).first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                },status=400)
            submitted_attachments = models.RPMSAttachment.objects.filter( is_submitted=True, class_work_id=class_work_id, employee_id=teacher_id).order_by('-created_at')
            unsubmitted_attachments = models.RPMSAttachment.objects.filter( is_submitted=False, class_work_id=class_work_id, employee_id=teacher_id).order_by('-created_at')
            
            return JsonResponse({
                    'teacher' : teacher.get_information(),
                    'submitted' : [attachment.get_information() for attachment in submitted_attachments],
                    'unsumitted' : [ attachment.get_information() for attachment in unsubmitted_attachments]
                },status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def evaluator_get_rpms_attachment_result(request):
    try:
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            rpms_folder_id = request.POST.get('rpms_folder_id')
            teacher_id = request.POST.get('teacher_id')
            
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'rpms_folder_id not found',
                },status=400) 
            
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id not found',
                },status=400)

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id , school_id=user.school_id  ).order_by('-created_at').first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS Folder not found',
                },status=400)

            classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at')
            if not classworks:
                return JsonResponse({
                    'message' : 'Classworks not found',
                },status=400)
                
            rpms_attachments = models.RPMSAttachment.objects.filter(class_work_id__in=[classwork.class_work_id for classwork in classworks], employee_id=teacher_id).order_by('-created_at')
            titles = []
            each_attachment_in_rpms = []
            for rpms_attachment in rpms_attachments:
                title = rpms_attachment.title
                if title not in titles:
                    titles.append(title)
                    each_attachment_in_rpms.append(
                        {
                            "title" : title,
                            "grade" : rpms_attachment.getGradeSummary()
                        }
                    )
            
            return JsonResponse({
                'rpms_folder_id' : rpms_folder_id,
                'scores' : each_attachment_in_rpms
            }, status=200)
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)





@csrf_exempt
def evaluator_summary_recommendations(request):
    try:
        
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id is required',
                    }, status=400)
            
            teacher = models.People.objects.filter(is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)
            
            
            result = my_utils.get_recommendation_result_with_percentage(employee_id=teacher.employee_id)
            
            return JsonResponse({
                'message' : 'Recommendation result found successfully',
                'result' : result,
            }, status=200)

    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)




@csrf_exempt
def evaluator_summary_performance(request):
    try:
        
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id is required',
                    }, status=400)

            teacher = models.People.objects.filter(is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)
                
            
            result = my_utils.get_performance_by_years(employee_id=teacher.employee_id)
            
            return JsonResponse({
                'message' : 'Performance result found successfully',
                'result' : result,
            }, status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def evaluator_summary_rpms(request):
    try:
        
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id is required',
                    }, status=400)

            teacher = models.People.objects.filter(is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            
            return JsonResponse( my_utils.get_kra_breakdown_of_a_teacher(employee_id=teacher.employee_id) , status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)




@csrf_exempt
def evaluator_summary_swot(request):
    try:
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id is required',
                    }, status=400)

            teacher = models.People.objects.filter(is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            strength = "The teacher has not been rated yet."
            weakness = "The teacher has not been rated yet."
            opportunity = "The teacher has not been rated yet."
            threat = "The teacher has not been rated yet."

            latest_cot = None
            cot_1 = models.COTForm.objects.filter(evaluated_id=teacher.employee_id, quarter="Quarter 1").order_by('-created_at').first()
            if cot_1:
                if cot_1.is_checked:
                    latest_cot = cot_1
            
            cot_2 = models.COTForm.objects.filter(evaluated_id=teacher.employee_id, quarter="Quarter 2").order_by('-created_at').first()
            if cot_2:
                if cot_2.is_checked:
                    latest_cot = cot_2
            
            cot_3 = models.COTForm.objects.filter(evaluated_id=teacher.employee_id, quarter="Quarter 3").order_by('-created_at').first()
            if cot_3:
                if cot_3.is_checked:
                    latest_cot = cot_3
            
            cot_4 = models.COTForm.objects.filter(evaluated_id=teacher.employee_id, quarter="Quarter 4").order_by('-created_at').first()
            if cot_4:
                if cot_4.is_checked:
                    latest_cot = cot_4
            
            if latest_cot:
                if not latest_cot.isAlreadyAIGenerated():
                    data = latest_cot.generatePromtTemplate() 
                    while True:
                        strength = my_utils.generate_text(data['strengths'])
                        if strength:
                            if len(strength) < 500: 
                                break
                    while True:       
                    
                        weakness = my_utils.generate_text(data['weaknesses'])
                        if weakness:
                            if len(weakness) < 500: 
                                break
                    while True:
                        opportunity = my_utils.generate_text(data['opportunities'])
                        if opportunity:
                            if len(opportunity) < 500: 
                                break
                            
                    while True: 
                        threat = my_utils.generate_text(data['threats'])
                        if threat:
                            if len(threat) < 500: 
                                break
                    
                    latest_cot.strengths_prompt = strength
                    latest_cot.weaknesses_prompt = weakness
                    latest_cot.opportunities_prompt = opportunity
                    latest_cot.threats_prompt = threat
                    latest_cot.save()
                     
                else :
                    strength = latest_cot.strengths_prompt
                    weakness = latest_cot.weaknesses_prompt
                    opportunity = latest_cot.opportunities_prompt
                    threat = latest_cot.threats_prompt
            
            
            return JsonResponse({ 
                'strength' : strength,
                'weakness' : weakness,
                'opportunity' : opportunity,
                'threat' : threat,
            }, status=200)
            
            
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def evaluator_get_records_cot(request):
    try:
        if request.method == "GET":
            
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            data = {
                "school_year" : [],
                "quarter" : [],
                "cot_taker" : [],
            }
            
            cots = models.COTForm.objects.filter(school_id=user.school_id).order_by('-created_at')
            for cot in cots:
                if cot.quarter not in data["quarter"]:
                    data["quarter"].append(cot.quarter)
                if cot.school_year not in data["school_year"]:
                    data["school_year"].append(cot.school_year)
                
                cot_taker = {
                    "school_year" : cot.school_year,
                    "quarter" : cot.quarter,
                    "cot_evaluator" : None,
                    "cot_taker" : None,
                    "cot" : cot.get_information(),
                }
                
                evaluator = models.People.objects.filter(employee_id=cot.employee_id).first()
                if evaluator:
                    cot_taker["cot_evaluator"] = evaluator.get_information()
                
                teacher = models.People.objects.filter(employee_id=cot.evaluated_id).first()
                if teacher:
                    cot_taker["cot_taker"] = teacher.get_information()
                
                data["cot_taker"].append(cot_taker)
            
            
            
            
            return JsonResponse(data, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
    'message' : 'Invalid request',
    }, status=400)




@csrf_exempt
def evaluator_get_records_rpms(request):
    try:
        if request.method == "GET":
            
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            data = {
                "school_year": [],
                "rpms_taker": [],
            }

            rpms = models.RPMSFolder.objects.filter(school_id=user.school_id).order_by('-created_at')
            for rpm in rpms:
                if rpm.rpms_folder_school_year not in data["school_year"]:
                    data["school_year"].append(rpm.rpms_folder_school_year)

                classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpm.rpms_folder_id, school_id=user.school_id).order_by('-created_at')
                for classwork in classworks:
                    attachment = models.RPMSAttachment.objects.filter(class_work_id=classwork.class_work_id, school_id=user.school_id).order_by('-created_at').first()
                    if attachment:
                        rpms_record = {
                            "school_year": rpm.rpms_folder_school_year,
                            "rpms_taker": None,
                            "rpms_data": attachment.get_information(),
                            "rpms_rater": None
                        }

                        rpms_taker = models.People.objects.filter(employee_id=attachment.employee_id, school_id=user.school_id).first()
                        if rpms_taker:
                            rpms_record["rpms_taker"] = rpms_taker.get_information()

                        rpms_rater = models.People.objects.filter(employee_id=attachment.evaluator_id, school_id=user.school_id).first()
                        if rpms_rater:
                            rpms_record["rpms_rater"] = rpms_rater.get_information()

                        data["rpms_taker"].append(rpms_record)

            return JsonResponse(data, status=200)

    except Exception as e:
        return JsonResponse({
            'message': f'Something went wrong: {e}',
        }, status=500)

    return JsonResponse({
        'message': 'Invalid request',
    }, status=400)



@csrf_exempt
def evaluator_get_records_ipcrf(request):
    try:
        if request.method == "GET":
            
            user = models.People.objects.filter(is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            

            data = {
                "school_year": [],
                "quarter": [],
                "ipcrf_taker": [],
            }

            ipcrfs = models.IPCRFForm.objects.filter(school_id=user.school_id, form_type="PART 1").order_by('-created_at')
            for ipcrf in ipcrfs:
                if ipcrf.school_year not in data["school_year"]:
                    data["school_year"].append(ipcrf.school_year)

                ipcrf_record = {
                    "school_year": ipcrf.school_year,
                    "ipcrf_taker": None,
                    "ipcrf_rater": None,
                    "ipcrf": ipcrf.get_information(),
                }

                ipcrf_taker = models.People.objects.filter(employee_id=ipcrf.employee_id, school_id=user.school_id).first()
                if ipcrf_taker:
                    ipcrf_record["ipcrf_taker"] = ipcrf_taker.get_information()

                ipcrf_rater = models.People.objects.filter(employee_id=ipcrf.evaluator_id, school_id=user.school_id).first()
                if ipcrf_rater:
                    ipcrf_record["ipcrf_rater"] = ipcrf_rater.get_information()

                data["ipcrf_taker"].append(ipcrf_record)

            return JsonResponse(data, status=200)

    except Exception as e:
        return JsonResponse({
            'message': f'Something went wrong: {e}',
        }, status=500)

    return JsonResponse({
        'message': 'Invalid request',
    }, status=400)




