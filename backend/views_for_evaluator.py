
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
                    'message' : 'Invalid employee_id or password',
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
                response_rate_of_ipcrf_1_proficient = number_of_evaluated_ipcrf_1_proficient / number_of_conducted_ipcrf_1_proficient
            else:
                response_rate_of_ipcrf_1_proficient = 0  # or handle this case as needed

            if number_of_conducted_ipcrf_1_highly_proficient != 0:
                response_rate_of_ipcrf_1_highly_proficient = number_of_evaluated_ipcrf_1_highly_proficient / number_of_conducted_ipcrf_1_highly_proficient
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
                response_rate_of_cot_proficient = number_of_evaluated_cot_proficient / number_of_conducted_cot_proficient
            else:
                response_rate_of_cot_proficient = 0  # or handle this case as needed

            if number_of_conducted_cot_highly_proficient != 0:
                response_rate_of_cot_highly_proficient = number_of_evaluated_cot_highly_proficient / number_of_conducted_cot_highly_proficient
            else:
                response_rate_of_cot_highly_proficient = 0  # or handle this case as needed

            
            
            rpms_proficient = models.RPMSAttachment.objects.filter(school_id=user.school_id, is_for_teacher_proficient=True).order_by('-created_at')
            rpms_highly_proficient = models.RPMSAttachment.objects.filter(school_id=user.school_id, is_for_teacher_proficient=False).order_by('-created_at')
            
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
                response_rate_of_rpms_proficient = number_of_evaluated_rpms_proficient / number_of_conducted_rpms_proficient
            else:
                response_rate_of_rpms_proficient = 0  # or handle this case as needed

            if number_of_conducted_rpms_highly_proficient != 0:
                response_rate_of_rpms_highly_proficient = number_of_evaluated_rpms_highly_proficient / number_of_conducted_rpms_highly_proficient
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
            
            teachers = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role='Teacher')
            labels = []
            ratings = []
            for teacher in teachers:
                labels.append(teacher.first_name)
                ipcrf_1 = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id, form_type='PART 1').order_by('-created_at').first()
                # cot_form = models.COTForm.objects.filter(evaluated_id=teacher.employee_id).order_by('-created_at').first()
                if ipcrf_1 :
                    if my_utils.is_proficient_faculty(teacher):
                        # ratings.append(my_utils.calculate_scores_for_proficient(ipcrf_1.content_for_teacher , cot_form.content))
                        ratings.append({
                            'average_score' : ipcrf_1.average_score,
                            'plus_factor' : ipcrf_1.plus_factor,
                            'total_score' : ipcrf_1.rating,
                        })
                    else:
                        # ratings.append(my_utils.calculate_scores_for_highly_proficient(ipcrf_1.content_for_teacher, cot_form.content))
                        ratings.append({
                            'average_score' : ipcrf_1.average_score,
                            'plus_factor' : ipcrf_1.plus_factor,
                            'total_score' : ipcrf_1.rating,
                        })
                else:
                    ratings.append({
                        'average_score' : 0,
                        'plus_factor' : 0,
                        'total_score' : 0
                    })
    
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

        
            people = People.objects.filter(role='Teacher', school_id=user.school_id)
            total_count = people.count()
            
            if total_count == 0:
                return JsonResponse({
                    '0-3 years': 0,
                    '3-5 years': 0,
                    '5+ years': 0
                }, status=200)

            # Initialize counters
            tenure_counts = {
                '0-3 years': 0,
                '3-5 years': 0,
                '5+ years': 0
            }

            for person in people:
                tenure_category = person.get_tenure_category()
                if tenure_category in tenure_counts:
                    tenure_counts[tenure_category] += 1
            
            # Calculate percentages
            tenure_percentages = {
                category: (count / total_count) * 100 for category, count in tenure_counts.items()
            }
            
            return JsonResponse({
                '0-3 years': tenure_percentages['0-3 years'],
                '3-5 years': tenure_percentages['3-5 years'],
                '5+ years': tenure_percentages['5+ years']
            }, status=200)
    
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
            
            
            number_of_promotion = 0
            number_of_termination = 0
            number_of_retention = 0
            
            teachers = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role='Teacher')
            for teacher in teachers:
                result = my_utils.get_recommendation_result(employee_id=teacher.employee_id)
                if result == 'PROMOTION':
                    number_of_promotion += 1
                elif result == 'TERMINATION':
                    number_of_termination += 1
                elif result == 'RETENTION':
                    number_of_retention += 1
            
            number_of_promotion = number_of_promotion / teachers.count() if teachers.count() > 0 else 0
            number_of_termination = number_of_termination / teachers.count() if teachers.count() > 0 else 0
            number_of_retention = number_of_retention / teachers.count() if teachers.count() > 0 else 0
            
            return JsonResponse({
                'promotion' : number_of_promotion,
                'termination' : number_of_termination,
                'retention' : number_of_retention
            }, status=200)
            
            
    
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
            
            
            teacher_performance = {}
            teachers = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role='Teacher')
            for teacher in teachers:
                teacher_performance[teacher.employee_id] = {}
                teacher_performance[teacher.employee_id]['Name'] = teacher.fullname
                teacher_performance[teacher.employee_id]['Performance'] = my_utils.get_employee_performance_by_year(teacher.employee_id , teacher.position)
            
            # {
            #     "Employee ID" : {
            #         "Name" : "Name",
            #         "Performance" :  {
            #             2021: {
            #                 'total_kra_score': 1.85,
            #                 'plus_factor': 0.02,
            #                 'total_score': 1.87
            #             },
            #             2022: {
            #                 'total_kra_score': 2.40,
            #                 'plus_factor': 0.04,
            #                 'total_score': 2.44
            #             },
            #             2023: {
            #                 'total_kra_score': 2.10,
            #                 'plus_factor': 0.03,
            #                 'total_score': 2.13
            #             }
            #         }
            #     } 
            # }
            
            return JsonResponse({
                'teacher_performance' : teacher_performance
            }, status=200) 
    
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

            cots = models.COTForm.objects.filter(evaluated_id=evaluator.employee_id, quarter=quarter , employee_id=teacher_id).order_by('-created_at').first()
            
            return JsonResponse({
                'cot' : cots.get_information(),
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
            
            
            
            subject = request.POST.get('subject')
            if not subject:
                return JsonResponse({
                    'message' : 'Subject is required',
                    'subject' : subject
                    }, status=400)
            
             
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
                employee_id=evaluator_id,
                cot_form_id=cot_id
            ).order_by('-created_at').first()
            
            if not cot_form:
                return JsonResponse({
                    'message' : 'COT form not found',
                }, status=400)
            
            my_utils.update_cot_form(cot_form=cot_form, comment=comments, questions=questions , content=content)
             
            if search_evaluated:
                search_evaluated.update_is_evaluted()
            
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
            
            part_1.evaluator_id = user.employee_id
            part_1.evaluator_rating = rating
            part_1.evaluator_plus_factor = plus_factor
            part_1.evaluator_average_score = average_score
            my_utils.update_ipcrf_form_part_1_by_evaluator(
                 ipcrf_form=part_1, content=content    
            )
             
            if teacher:
                teacher.update_is_evaluted()
            
            return JsonResponse({
                'message' : 'Form updated successfully',
            },status=200)
            
            
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


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
            
            if not rpms_id:
                return JsonResponse({
                   'message' : 'Please provide RPMS ID',
                    }, status=400)
            
            if not content:
                return JsonResponse({
                    'message' : 'Content is required',
                    }, status=400)
            
            rpms = models.RPMSAttachment.objects.filter(attachment_id=rpms_id).order_by('-created_at').first()
            if not rpms:
                return JsonResponse({
                    'message' : 'Invalid RPMS ID',
                    }, status=400)
            
            my_utils.update_rpms_attachment(rpms=rpms, content=content)
            
            teacher = models.People.objects.filter(is_accepted = True, employee_id=rpms.employee_id, role='Teacher').first()
            if teacher:
                teacher.update_is_evaluted()
            
            return JsonResponse({
                'message' : 'Form updated successfully',
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
    
    