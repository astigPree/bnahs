
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
            
            user = models.People.objects.filter( is_deactivated = False, is_accepted = True, employee_id=employee_id, password=password).first()
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
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username, role='Evaluator').first()
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
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username).first()
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
                
            teachers = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, role='Teacher').order_by('-created_at')
            
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
        if request.method == 'POST':
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username).first()
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
            
            school_year = request.POST.get('school_year' , None)
            
            
            teachers = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, role='Teacher').order_by('-created_at')
            if not teachers:
                return JsonResponse(teachers_ratings, status=400)
            
            for teacher in teachers:
                
                if school_year:
                    ipcrf_1 = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id, form_type='PART 1' , school_year=school_year).order_by('-created_at').first() 
                else:
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
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username, role='Evaluator').first()
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

            people = People.objects.filter(is_deactivated = False,  is_accepted = True, role='Teacher', school_id=user.school_id)
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
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username).first()
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
            teachers = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, role='Teacher')
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
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username).first()
            # TODO : IDENTIFY IF THE USER IS EVALUATOR OR NOT
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            teachers = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, role='Teacher') 
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
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username).first()
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
            evaluator = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username).first()
            if not evaluator:
                return JsonResponse({
                    'message' : 'Evaluator not found',
                    }, status=400)

            teacher_id = request.POST.get('teacher_id')
            quarter = request.POST.get('quarter')
            # cot_id = request.POST.get('cot_id')
            
            # if not cot_id:
            #     return JsonResponse({
            #         'message' : 'cot_id is required',
            #         }, status=400) 
            
            if not teacher_id:
                return JsonResponse({
                    'message' : 'Teacher ID is required',
                    }, status=400)
            
            if not quarter:
                return JsonResponse({
                    'message' : 'Quarter is required',
                    }, status=400)
            
            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=evaluator.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            cots = models.COTForm.objects.filter(school_id=evaluator.school_id, quarter=quarter , evaluated_id=teacher_id).order_by('-created_at').first()
            
            rater = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=evaluator.school_id, employee_id=cots.employee_id).first()
            
            return JsonResponse({
                'cot' : cots.get_information() if cots else {},
                'teacher' : teacher.get_information(),
                'rater' : rater.get_information() if rater else None
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
            
            search_evaluator = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=evaluator_id, role='Evaluator').first()
            if not search_evaluator:
                return JsonResponse({
                    'message' : 'Evaluator not found',
                }, status=400)
            
            search_evaluated = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=evaluated_id, role='Teacher').first()
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
                        
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username, role='Evaluator').first()
            if not user:
                return JsonResponse({
                   'message' : 'User not found',
                    }, status=400)
            
            
            ipcrf_forms_for_proficient = models.IPCRFForm.objects.filter( school_id=user.school_id , is_for_teacher_proficient=True , form_type="PART 1").order_by('-created_at')
            
            proficient_employee_ids = []
            ipcrf_forms_data_proficient = []
            for ipcrf_form in ipcrf_forms_for_proficient:
                if ipcrf_form.employee_id not in proficient_employee_ids:
                    if user.department == "N/A":
                        teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=ipcrf_form.employee_id, role='Teacher').first()
                    else :
                        teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=ipcrf_form.employee_id, role='Teacher', department=user.department).first()
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
                    
                    if user.department == "N/A":
                        teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=ipcrf_form.employee_id, role='Teacher').first()
                    else :
                        teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=ipcrf_form.employee_id, role='Teacher', department=user.department).first()
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
            
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username, role='Evaluator').first()
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
