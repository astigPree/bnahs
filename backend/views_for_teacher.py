
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
            remember_me = request.POST.get('remember_me', False)
            
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
            
            # Fetch filtered data
            ipcrf_forms = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1').order_by('-created_at')  # Apply your filters here
            cot_forms = models.COTForm.objects.filter(employee_id=user.employee_id).order_by('-created_at')  # Apply your filters here
            rpms_attachments = models.RPMSAttachment.objects.filter(employee_id=user.employee_id).order_by('-created_at')  # Apply your filters here

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
             
            
            return JsonResponse({
                'kba_breakdown' : my_utils.get_kra_breakdown_of_a_teacher(employee_id=user.employee_id),
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
            ipcrf_forms = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1').order_by('-created_at')
            scores = [ form.getEvaluatorPart1Scores() for form in ipcrf_forms ]
            
            # Initialize counters
            
            promotion_count = 0
            retention_count = 0
            termination_count = 0
            overall_scores = []
            detailed_scores = []  # To hold detailed score information
            print("Scores : ", scores)
            # Classify scores
            for score in scores:
                print("This is the score : ", score)
                # for _, value in score.items():
                #     average_score = value['Average']    
                #     overall_scores.append(average_score)
                #     category = my_utils.classify_ipcrf_score(average_score if average_score else 0)
                #     detailed_scores.append({
                #         'Average': average_score,
                #         'Category': category
                #     })
                #     if category == 'Outstanding':
                #         promotion_count += 1
                #     elif category in ['Very Satisfactory', 'Satisfactory']:
                #         retention_count += 1
                #     elif category in ['Unsatisfactory', 'Poor']:
                #         termination_count += 1
                average_score = score['average_score']
                overall_scores.append(average_score)
                category = my_utils.classify_ipcrf_score(average_score if average_score else 0)
                detailed_scores.append({
                        'Average': average_score,
                        'Category': category
                    })
                if category == 'Outstanding':
                        promotion_count += 1
                elif category in ['Very Satisfactory', 'Satisfactory']:
                        retention_count += 1
                elif category in ['Unsatisfactory', 'Poor']:
                        termination_count += 1
                
                
            # Calculate percentages
            total = len(overall_scores)
            promotion_percentage = promotion_count / total * 100 if total > 0 else 0
            retention_percentage = retention_count / total * 100 if total > 0 else 0
            termination_percentage = termination_count / total * 100 if total > 0 else 0

            # Create recommendation dictionary
            recommendation = {
                'Promotion': promotion_percentage,
                'Retention': retention_percentage,
                'Termination': termination_percentage
            }

            # Calculate overall classification
            overall_average = sum(overall_scores) / total if total > 0 else 0
            overall_classification = my_utils.classify_ipcrf_score(overall_average)
            
            # Get The Recommended Rank
            rank = my_utils.recommend_rank(user)
            
            """
                {
                    "recommendation": {
                        "Promotion": 33.33,
                        "Retention": 33.33,
                        "Termination": 33.33
                    },
                    "detailed_scores": [
                        {"Average": 4.8, "Category": "Outstanding"},
                        {"Average": 4.5, "Category": "Outstanding"},
                        {"Average": 3.9, "Category": "Very Satisfactory"},
                        {"Average": 3.7, "Category": "Very Satisfactory"},
                        {"Average": 2.2, "Category": "Unsatisfactory"},
                        {"Average": 1.8, "Category": "Unsatisfactory"}
                    ],
                    "overall": {
                        "Average": 3.48,
                        "Classification": "Satisfactory"
                    },
                    "working years" : "5 years",
                    "current position" : "Teacher I",
                    "recommended position" : "Teacher II"
                 } 
            """
            # Return JSON response
            return JsonResponse({
                'recommendation': recommendation,
                'detailed_scores': detailed_scores,
                'overall': {
                    'Average': overall_average,
                    'Classification': overall_classification
                },
                'working years' : f"{user.working_years()} years",
                "current position" : user.position,
                "recommended position" : rank
            }, status=200)
    
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
            # Check if the user is a teacher

            # Annotate the IPCRF forms with the year of submission
            attachments = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1').order_by('-created_at').annotate(year=ExtractYear('created_at'))
            
            # Initialize the performances dictionary
            performances = {}
            
            # Loop through the attachments and gather scores by year
            for attachment in attachments:
                year = attachment.year
                if year not in performances:
                    performances[year] = {'Scores': [], 'Total': 0}
                
                scores = attachment.getEvaluatorPart1Scores()
                performances[year]['Score'] = scores['average_score']
                # for key, value in scores.items():
                    # if 'Average' in value:
                    #     performances[year]['Scores'].append(value['Average'])
                    
            
            # Calculate the total for each year
            years = sorted(performances.keys())
            total_scores = []
            for year in years:
                total = sum(performances[year]['Scores'])
                performances[year]['Total'] = total
                total_scores.append(total)

            # Convert to labels and data suitable for the chart
            labels = [str(year) for year in years]
            data = total_scores
            
            """
            {
                "performance": {
                    "labels": ["2022", "2023"],
                    "data": [16.33, 9.33]
                }
            }
            """
            return JsonResponse({'performance': {'labels': labels, 'data': data}}, status=200)
                    
        
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
            cot_form = models.COTForm.objects.filter(employee_id=user.employee_id).order_by('-created_at').first()
            generated_swot = {
                'Strengths': '',
                'Weaknesses': '',
                'Opportunities': '',
                'Threats': ''
            }
            if cot_form:
                swot = cot_form.generatePromtTemplate()
                generated_swot["Strengths"] = my_utils.my_utils(swot["strengths"])
                generated_swot["Weaknesses"] = my_utils.generate_text(swot["weaknesses"])
                generated_swot["Opportunities"] = my_utils.generate_text(swot["opportunities"])
                generated_swot["Threats"] = my_utils.generate_text(swot["threats"])
            
            
            
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
            
            if not content:
                return JsonResponse({
                    'message' : 'Content not found',
                }, status=400)
            
            ipcrf.rating = rating
            ipcrf.plus_factor = plus_factor
            ipcrf.average_score = average_score
            my_utils.update_iprcf_form_part_1_by_teacher(ipcrf, content)
            
            return JsonResponse({
                'message' : 'IPCRF Form updated successfully',
                'connection_to_other' : ipcrf.connection_to_other
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
            
            ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type='PART 2').order_by('-created_at').first()
            if not ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form not found',
                }, status=400)
            
            if not content:
                return JsonResponse({
                    'message' : 'Content not found',
                }, status=400)
                
            my_utils.update_ipcrf_form_part_2_by_teacher(ipcrf, content)
            
            return JsonResponse({
                'message' : 'IPCRF Form updated successfully',
                'connection_to_other' : ipcrf.connection_to_other
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
            
            ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type='PART 3').order_by('-created_at').first()
            if not ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form not found',
                }, status=400)
            
            if not content:
                return JsonResponse({
                    'message' : 'Content not found',
                }, status=400)
                
            my_utils.update_ipcrf_form_part_3_by_teacher(ipcrf, content)
            
            return JsonResponse({
                'message' : 'IPCRF Form updated successfully',
                'connection_to_other' : ipcrf.connection_to_other
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
                employee_id=user.employee_id, 
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
                'rpms_folder' : rpms_folder,
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
            
            class_work_id = request.POST.get('class_work_id')
            rpms_attachment = request.FILES.get('rpms_attachment')
            
            
            if not class_work_id:
                return JsonResponse({
                    'message' : 'class_work_id not found',
                },status=400)
            
            if not rpms_attachment:
                return JsonResponse({
                    'message' : 'rpms_attachment not found',
                },status=400)
            
            classwork = models.RPMSClassWork.objects.filter(class_work_id=class_work_id).order_by('-created_at').first()
            if not classwork:
                return JsonResponse({
                    'message' : 'Class Work not found',
                },status=400)

            
            attachment = models.RPMSAttachment.objects.create(
                school_id=user.school_id,
                employee_id=user.employee_id,
                class_work_id=class_work_id, # IDENTIFIER FOR WHAT TYPE OF CLASSWORK
                file=rpms_attachment
            )
            
            attachment.title = classwork.title
            attachment.grade = classwork.get_grade()
            attachment.attachment_id = str(uuid4())
            attachment.save()
            
            return JsonResponse({
                'message' : 'File uploaded successfully',
            },status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_submit_rpms_work(request):
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
            
            attachments = models.RPMSAttachment.objects.filter(class_work_id=class_work_id, employee_id=user.employee_id).order_by('-created_at')
            
            return JsonResponse({
                    'classwork' : [attachment.get_information() for attachment in attachments],
                    'completed' : attachments.count() == 6 if attachments else False
                },status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)









