
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
from django.utils import timezone 

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
            remember_me = request.POST.get('remember_me', False)
            
            if not employee_id or not password:
                return JsonResponse({
                    'message' : 'Please provide employee_id and password',
                    }, status=400)
            
            user = models.People.objects.filter(is_accepted = True, employee_id=employee_id, password=password).first()
            if not user:
                return JsonResponse({
                    'message' : 'Invalid employee_id or password',
                    }, status=400)
            
            # TODO : CHECK IF THE USER IS TEACHER OR NOT
            if user.role != 'Teacher':
                return JsonResponse({
                    'message' : 'User is not a teacher',
                    }, status=400)
            
            
            user_authenticated = authenticate(request, username=employee_id, password=password)
            if not user_authenticated:
                return JsonResponse({
                    'message' : 'Invalid employee_id or password in authentication',
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
            
            ipcrf_data = {
                'part_1' : False,
                'part_1_rater' : False,
                'part_2' : False,
                'part_3' : False,
                'overall' : False,
                'rater' : None,
                'content' : None,
                'rater' : None,
                'date_submitted' : None,
            }
            ipcrf_1 = models.IPCRFForm.objects.filter(employee_id=user.employee_id, school_id=user.school_id, form_type="PART 1").first()
            if ipcrf_1:
                ipcrf_data['content'] = ipcrf_1.get_information()
                ipcrf_data['part_1'] = ipcrf_1.is_checked
                ipcrf_data['part_1_rater'] = ipcrf_1.is_checked_by_evaluator
                if ipcrf_1.is_checked_by_evaluator:
                    rater = models.People.objects.filter(employee_id=ipcrf_1.evaluator_id).first()
                    ipcrf_data['date_submitted'] = ipcrf_1.created_at
                    if rater:
                        ipcrf_data['rater'] = rater.get_information()
            ipcrf_2 = models.IPCRFForm.objects.filter(employee_id=user.employee_id, school_id=user.school_id, form_type="PART 2").first()
            if ipcrf_2:
                ipcrf_data['part_2'] = ipcrf_2.is_checked 
            
            ipcrf_3 = models.IPCRFForm.objects.filter(employee_id=user.employee_id, school_id=user.school_id, form_type="PART 3").first()
            if ipcrf_3:
                ipcrf_data['part_3'] = ipcrf_3.is_checked 
                
            ipcrf_data['overall'] = all([ipcrf_data['part_1'], ipcrf_data['part_1_rater'], ipcrf_data['part_2'], ipcrf_data['part_3']])
            
            
            cots_data = {
                'quarter_1': False,
                'quarter_2' : False,
                'quarter_3' : False,
                'quarter_4' : False,
                'overall' : False,
                'content_1' : None,
                'content_2' : None,
                'content_3' : None,
                'content_4' : None,
                'rater' : None, 
                "date_submitted" : None
            }
            
            cots_1 = models.COTForm.objects.filter(evaluated_id=user.employee_id, school_id=user.school_id, quarter="Quarter 1").first()
            if cots_1:
                cots_data['quarter_1'] = cots_1.is_checked
                cots_data['content_1'] = cots_1.get_information()
                cots_data['date_submitted'] = cots_1.created_at
                
                rater = models.People.objects.filter(employee_id=cots_1.employee_id).first()
                if rater:
                    cots_data['rater'] = rater.get_information()
                    
            cots_2 = models.COTForm.objects.filter(evaluated_id=user.employee_id,  school_id=user.school_id, quarter="Quarter 2").first()
            if cots_2:
                cots_data['quarter_2'] = cots_2.is_checked 
                cots_data['content_2'] = cots_2.get_information()
                
            cots_3 = models.COTForm.objects.filter(evaluated_id=user.employee_id,  school_id=user.school_id, quarter="Quarter 3").first()
            if cots_3:
                cots_data['quarter_3'] = cots_3.is_checked 
                cots_data['content_3'] = cots_3.get_information()
                
            cots_4 = models.COTForm.objects.filter(evaluated_id=user.employee_id, school_id=user.school_id, quarter="Quarter 4").first()
            if cots_4:
                cots_data['quarter_4'] = cots_4.is_checked 
                cots_data['content_4'] = cots_4.get_information()
                
            cots_data['overall'] = all([cots_data['quarter_1'], cots_data['quarter_2'], cots_data['quarter_3'], cots_data['quarter_4']])
            
            rpms_data = {
                'overall' : False,
                "rater" : None,
                "date_submitted" : None
            }
            
            folder = models.RPMSFolder.objects.filter(school_id=user.school_id, is_for_teacher_proficient=True if my_utils.is_proficient_faculty(user) else False ).order_by('-created_at').first()
            if folder:
                rpms_data['folder'] = folder.get_rpms_folder_information() 
                classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=folder.rpms_folder_id).order_by('-created_at')
                submitted_all = 0
                rpms_data['date_submitted'] = folder.created_at
                for classwork in classworks:
                    rpms_data[classwork.title + " id"] = classwork.get_rpms_classwork_information()
                    rpms_data[classwork.title] = None
                    attachment = models.RPMSAttachment.objects.filter(class_work_id=classwork.class_work_id, employee_id=user.employee_id).order_by('-created_at').first()
                    if attachment:
                        if attachment.is_checked:
                            submitted_all += 1
                            rater = models.People.objects.filter(employee_id=attachment.evaluator_id).first()
                            if rater:
                                rpms_data["rater"] = rater.get_information()
                        rpms_data[classwork.title] = attachment.get_information()
                            
                rpms_data['overall'] = submitted_all == len(classworks)

                        
            
            return JsonResponse({ 
                'teacher' : user.get_information(),
                'ipcrf' : ipcrf_data,
                'cots' : cots_data,
                'rpms' : rpms_data, 
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
                'Proficient' : my_utils.is_proficient_faculty(user)
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
             
            
            
            return JsonResponse( my_utils.get_kra_breakdown_of_a_teacher(employee_id=user.employee_id) , status=200)
    
    
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
                
            result = my_utils.get_recommendation_result_with_percentage(employee_id=user.employee_id)
            
            return JsonResponse({
                'message' : 'Recommendation result found successfully',
                'result' : result,
            }, status=200)
             
            # # 2. rule based classifier for Promotion
            # ipcrf_forms = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1').order_by('-created_at')
            # scores = [ form.getEvaluatorPart1Scores() for form in ipcrf_forms  ]
            
            # # Initialize counters
            
            # promotion_count = 0
            # retention_count = 0
            # termination_count = 0
            # overall_scores = []
            # detailed_scores = []  # To hold detailed score information 
            # # Classify scores
            # for score in scores: 
            #     # for _, value in score.items():
            #     #     average_score = value['Average']    
            #     #     overall_scores.append(average_score)
            #     #     category = my_utils.classify_ipcrf_score(average_score if average_score else 0)
            #     #     detailed_scores.append({
            #     #         'Average': average_score,
            #     #         'Category': category
            #     #     })
            #     #     if category == 'Outstanding':
            #     #         promotion_count += 1
            #     #     elif category in ['Very Satisfactory', 'Satisfactory']:
            #     #         retention_count += 1
            #     #     elif category in ['Unsatisfactory', 'Poor']:
            #     #         termination_count += 1 
            #     if score is not None:
            #         average_score = score.get('average_score', 0) 
            #     else :
            #         average_score = 0
            #     overall_scores.append(average_score)
            #     category = my_utils.classify_ipcrf_score(average_score if average_score else 0)
            #     detailed_scores.append({
            #             'Average': average_score,
            #             'Category': category
            #         })
            #     if category == 'Outstanding':
            #             promotion_count += 1
            #     elif category in ['Very Satisfactory', 'Satisfactory']:
            #             retention_count += 1
            #     elif category in ['Unsatisfactory', 'Poor']:
            #             termination_count += 1
                
                
            # # Calculate percentages
            # total = len(overall_scores)
            # promotion_percentage = promotion_count / total * 100 if total > 0 else 0
            # retention_percentage = retention_count / total * 100 if total > 0 else 0
            # termination_percentage = termination_count / total * 100 if total > 0 else 0

            # # Create recommendation dictionary
            # recommendation = {
            #     'Promotion': promotion_percentage,
            #     'Retention': retention_percentage,
            #     'Termination': termination_percentage
            # }

            # # Calculate overall classification
            # overall_average = sum(overall_scores) / total if total > 0 else 0
            # overall_classification = my_utils.classify_ipcrf_score(overall_average)
            
            # # Get The Recommended Rank
            # rank = my_utils.recommend_rank(user)
            
            # """
            #     {
            #         "recommendation": {
            #             "Promotion": 33.33,
            #             "Retention": 33.33,
            #             "Termination": 33.33
            #         },
            #         "detailed_scores": [
            #             {"Average": 4.8, "Category": "Outstanding"},
            #             {"Average": 4.5, "Category": "Outstanding"},
            #             {"Average": 3.9, "Category": "Very Satisfactory"},
            #             {"Average": 3.7, "Category": "Very Satisfactory"},
            #             {"Average": 2.2, "Category": "Unsatisfactory"},
            #             {"Average": 1.8, "Category": "Unsatisfactory"}
            #         ],
            #         "overall": {
            #             "Average": 3.48,
            #             "Classification": "Satisfactory"
            #         },
            #         "working years" : "5 years",
            #         "current position" : "Teacher I",
            #         "recommended position" : "Teacher II"
            #      } 
            # """
            # # Return JSON response
            # return JsonResponse({
            #     'recommendation': recommendation,
            #     'detailed_scores': detailed_scores,
            #     'overall': {
            #         'Average': overall_average,
            #         'Classification': overall_classification
            #     },
            #     'working years' : f"{user.working_years()} years",
            #     "current position" : user.position,
            #     "recommended position" : rank,
            # }, status=200)
    
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
            
            user = models.People.objects.filter(employee_id=request.user.username , role='Teacher').first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            result = my_utils.get_performance_by_years(employee_id=user.employee_id)
            
            return JsonResponse({
                'message' : 'Performance result found successfully',
                'result' : result,
            }, status=200)
            
            
            
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
            # # Check if the user is a teacher

            # # Annotate the IPCRF forms with the year of submission
            # attachments = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1').order_by('-created_at').annotate(year=ExtractYear('created_at'))
            
            # # Initialize the performances dictionary
            # performances = {}
            
            # # Loop through the attachments and gather scores by year
            # for attachment in attachments:
            #     year = attachment.year
            #     if year not in performances:
            #         performances[year] = {'Scores': [], 'Total': 0}
                
            #     scores = attachment.getEvaluatorPart1Scores() if attachment else {}
            #     if scores is not None: 
            #         performances[year]['Score'] =  scores.get('average_score', 0)
            #     else : 
            #         performances[year]['Score'] = 0 
            #     # for key, value in scores.items():
            #         # if 'Average' in value:
            #         #     performances[year]['Scores'].append(value['Average'])
                    
            
            # # Calculate the total for each year
            # years = sorted(performances.keys())
            # total_scores = []
            # for year in years:
            #     total = sum(performances[year]['Scores'])
            #     performances[year]['Total'] = total
            #     total_scores.append(total)

            # # Convert to labels and data suitable for the chart
            # labels = [str(year) for year in years]
            # data = total_scores
            
            # """
            # {
            #     "performance": {
            #         "labels": ["2022", "2023"],
            #         "data": [16.33, 9.33]
            #     }
            # }
            # """
            # return JsonResponse({'performance': {'labels': labels, 'data': data}}, status=200)
                    
        
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
            
         
            strength = "The teacher has not been rated yet."
            weakness = "The teacher has not been rated yet."
            opportunity = "The teacher has not been rated yet."
            threat = "The teacher has not been rated yet."

            latest_cot = None
            cot_1 = models.COTForm.objects.filter(evaluated_id=user.employee_id, quarter="Quarter 1").order_by('-created_at').first()
            if cot_1:
                if cot_1.is_checked:
                    latest_cot = cot_1
            
            cot_2 = models.COTForm.objects.filter(evaluated_id=user.employee_id, quarter="Quarter 2").order_by('-created_at').first()
            if cot_2:
                if cot_2.is_checked:
                    latest_cot = cot_2
            
            cot_3 = models.COTForm.objects.filter(evaluated_id=user.employee_id, quarter="Quarter 3").order_by('-created_at').first()
            if cot_3:
                if cot_3.is_checked:
                    latest_cot = cot_3
            
            cot_4 = models.COTForm.objects.filter(evaluated_id=user.employee_id, quarter="Quarter 4").order_by('-created_at').first()
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
def teacher_get_ipcrf_part_1(request):
    try:
        
        if request.method == 'GET':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            ipcrf = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1').order_by('-created_at').first()
            if not ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form not found',
                }, status=400)

            return JsonResponse({
                'ipcrf' : ipcrf.get_information(),
            },status=200)
        
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    
    
@csrf_exempt
def teacher_update_ipcrf_part_1(request):
    try:
        
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            """
                {
                    'ipcrf_id' : 'ipcrf_id',
                    'content' : {...} !Content/Checked of IPCRF form from teacher,
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
            
            
            ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type='PART 1').order_by('-created_at').first()
            if not ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form not found',
                }, status=400)
            
            if ipcrf.is_checked:
                return JsonResponse({
                    'message' : 'IPCRF Form is already checked',
                }, status=400)
            
            ipcrf.submit_date = timezone.now()
            ipcrf.rating = rating
            ipcrf.plus_factor = plus_factor
            ipcrf.average_score = average_score
            my_utils.update_iprcf_form_part_1_by_teacher(ipcrf, content)
            
            evaluation = ""
            if not user.is_evaluated:
                evaluation = user.update_is_evaluted()
                
            
            return JsonResponse({
                'message' : 'IPCRF Form updated successfully',
                'connection_to_other' : ipcrf.connection_to_other,
                'evaluation' : evaluation,
            },status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_get_ipcrf_part_2(request):
    try:
        
        if request.method == 'GET':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            ipcrf = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 2').order_by('-created_at').first()
            if not ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form not found',
                }, status=400)

            return JsonResponse({
                'ipcrf' : ipcrf.get_information(),
            },status=200)
        
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    

@csrf_exempt
def teacher_update_ipcrf_part_2(request):
    try:
        
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            """
                {
                    'ipcrf_id' : 'ipcrf_id',
                    'content' : {...} !Content/Checked of IPCRF form from teacher
                }
            """
            
            connection_to_other = request.POST.get('ipcrf_id')
            content : dict[str , dict] = json.loads(request.POST.get('content', None))
            
            if not content:
                return JsonResponse({
                    'message' : 'Content not found',
                }, status=400)
            
            ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type='PART 2').order_by('-created_at').first()
            if not ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form not found',
                }, status=400)
                
            if ipcrf.is_checked:
                return JsonResponse({
                    'message' : 'IPCRF Form is already checked',
                }, status=400)
                
            part_1_ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type='PART 1').order_by('-created_at').first()
            if not part_1_ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form PART 1 not found',
                }, status=400)
            
            if not part_1_ipcrf.is_checked:
                return JsonResponse({
                    'message' : 'IPCRF Form PART 1 is not checked',
                }, status=400)
            
            
            ipcrf.submit_date = timezone.now()
            my_utils.update_ipcrf_form_part_2_by_teacher(ipcrf, content)
            evaluation = ""
            if not user.is_evaluated:
                evaluation = user.update_is_evaluted()
            return JsonResponse({
                'message' : 'IPCRF Form updated successfully',
                'connection_to_other' : ipcrf.connection_to_other,
                'evaluation' : evaluation,
            },status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_get_ipcrf_part_3(request):
    try:
        
        if request.method == 'GET':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            ipcrf = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 3').order_by('-created_at').first()
            if not ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form not found',
                }, status=400)

            return JsonResponse({
                'ipcrf' : ipcrf.get_information(),
            },status=200)
        
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_update_ipcrf_part_3(request): 
    try:
        
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            """
                {
                    'ipcrf_id' : 'ipcrf_id',
                    'content' : {...} !Content/Checked of IPCRF form from teacher
                }
            """
            
            connection_to_other = request.POST.get('ipcrf_id')
            content : dict[str , dict] = json.loads(request.POST.get('content', None))
            
            if not content:
                return JsonResponse({
                    'message' : 'Content not found',
                }, status=400)
                
            ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type='PART 3').order_by('-created_at').first()
            if not ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form not found',
                }, status=400)
            
            if ipcrf.is_checked:
                return JsonResponse({
                    'message' : 'IPCRF Form is already checked',
                }, status=400)
            
            part_1_ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type="PART 1").first()
            if not part_1_ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form PART 1 not found',
                }, status=400)
            
            if not part_1_ipcrf.is_checked:
                return JsonResponse({
                    'message' : 'IPCRF Form PART 1 is not checked',
                }, status=400)
            
            part_2_ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type="PART 2").first()
            if not part_2_ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form PART 2 not found',
                }, status=400)
            
            if not part_2_ipcrf.is_checked:
                return JsonResponse({
                    'message' : 'IPCRF Form PART 2 is not checked',
                }, status=400)
            
            ipcrf.submit_date = timezone.now()
            my_utils.update_ipcrf_form_part_3_by_teacher(ipcrf, content)
            evaluation = ""
            if not user.is_evaluated:
                evaluation = user.update_is_evaluted()
            return JsonResponse({
                'message' : 'IPCRF Form updated successfully',
                'connection_to_other' : ipcrf.connection_to_other,
                'evaluation' : evaluation,
            },status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def teacher_get_rpms_folders(request):
    # Used to view all the folder
    try:
        
        if request.method == 'GET':
            user = models.People.objects.filter(employee_id=request.user.username, role='Teacher').first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            rpms_folders = models.RPMSFolder.objects.filter(
                school_id=user.school_id,
                is_for_teacher_proficient=my_utils.is_proficient_faculty(user)
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
def teacher_get_rpms_folder(request):
    try:
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first()

            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)

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
def teacher_get_rpms_work(request):
    try:
        
        if request.method == 'POST':
            
            user = models.People.objects.filter(employee_id=request.user.username, role='Teacher').first()

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
def teacher_turn_in_rpms_work(request): 
    try:
        
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            files = []
            class_work_id = request.POST.get('class_work_id')
            file = request.FILES.get('file')
            if file:
                files.append(file)
            # i = 0
            # while True:
            #     file = request.FILES.get(f'file{i}')
            #     if not file:
            #         break
            #     files.append(file)
            #     i += 1
            
            
            if not class_work_id:
                return JsonResponse({
                    'message' : 'class_work_id not found',
                },status=400)
            
            if not files or len(files) == 0:
                return JsonResponse({
                    'message' : 'files not found or empty files used name convention "file" ',
                },status=400)
            
            classwork = models.RPMSClassWork.objects.filter(class_work_id=class_work_id).order_by('-created_at').first()
            if not classwork:
                return JsonResponse({
                    'message' : 'Class Work not found',
                },status=400)
                
            folder = models.RPMSFolder.objects.filter(rpms_folder_id=classwork.rpms_folder_id).order_by('-created_at').first()
            if not folder:
                return JsonResponse({
                    'message' : 'Folder not found',
                },status=400)
            
            past_attachments = models.RPMSAttachment.objects.filter( is_submitted=True, employee_id=user.employee_id, class_work_id=class_work_id).order_by('-created_at')
            
            if past_attachments:
                return JsonResponse({
                    'message' : 'Unsubmit before adding new ',
                },status=400)
            
            past_attachments = models.RPMSAttachment.objects.filter( is_submitted=False, employee_id=user.employee_id, class_work_id=class_work_id).order_by('-created_at').first()
            
            attachment_id = past_attachments.attachment_id if past_attachments else str(uuid4())
            post_id = past_attachments.post_id if past_attachments else str(uuid4())
            
            for file in files:
                attachment = models.RPMSAttachment.objects.create(
                    school_id=user.school_id,
                    employee_id=user.employee_id,
                    class_work_id=class_work_id, # IDENTIFIER FOR WHAT TYPE OF CLASSWORK
                    file=file,
                    is_submitted = True
                )
                
                attachment.submit_date = timezone.now()
                attachment.is_for_teacher_proficient = my_utils.is_proficient_faculty(user)
                attachment.title = classwork.title
                attachment.grade = classwork.get_grade()
                attachment.attachment_id = attachment_id
                attachment.post_id = post_id
                attachment.save()
            
            return JsonResponse({
                'message' : 'Files uploaded successfully',
            },status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_get_rpms_work_attachments(request):
    try:
        
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            class_work_id = request.POST.get('class_work_id')
            
            if not class_work_id:
                return JsonResponse({
                    'message' : 'class_work_id not found',
                },status=400)
            
            submitted_attachments = models.RPMSAttachment.objects.filter( is_submitted=True, class_work_id=class_work_id, employee_id=user.employee_id).order_by('-created_at')
            unsubmitted_attachments = models.RPMSAttachment.objects.filter( is_submitted=False, class_work_id=class_work_id, employee_id=user.employee_id).order_by('-created_at')
            
            return JsonResponse({
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
def teacher_get_rpms_attachment_result(request):
    try:
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if 'Teacher' != user.role:
                return JsonResponse({
                    'message' : 'User not found',
                },status=400)
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            rpms_folder_id = request.POST.get('rpms_folder_id')
            
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'rpms_folder_id not found',
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
                
            rpms_attachments = models.RPMSAttachment.objects.filter(class_work_id__in=[classwork.class_work_id for classwork in classworks], employee_id=user.employee_id).order_by('-created_at')
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
def teacher_unsubmit_class_work(request):
    try:
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            class_work_id = request.POST.get('class_work_id')

            if not class_work_id:
                return JsonResponse({
                    'message' : 'class_work_id not found',
                },status=400)
            
            
            attachments = models.RPMSAttachment.objects.filter(class_work_id=class_work_id, is_submitted=True, employee_id=user.employee_id).order_by('-created_at')
            for attachment in attachments:
                attachment.is_submitted = False
                attachment.save()
            
            return JsonResponse({
                'message' : 'Files unsubmitted successfully',
            },status=200)
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)






@csrf_exempt
def teacher_generate_report(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            data = {
                
            }
            
            data['job'] = user.get_job_years()
            data['recommendation'] = my_utils.get_recommendation_result_with_percentage(employee_id=user.employee_id)
            
            ipcrf = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1').order_by('-created_at').first()
            data['rating'] = ipcrf.get_information() if ipcrf else None
            data['performance_rating'] = my_utils.classify_ipcrf_score(ipcrf.evaluator_rating if ipcrf else 0.0)
            data['ranking'] = my_utils.recommend_rank(user)
            data['teacher'] = user.get_information()
            data['rater'] = None
            if ipcrf:
                rater = models.People.objects.filter(employee_id=ipcrf.evaluator_id).first()
                if rater:
                    data['rater'] = rater.get_information()
            
            return JsonResponse(data,status=200)
            
    
    except Exception as e: 
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400 )



