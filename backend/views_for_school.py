
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




    
# ================================= School Views ============================== # 

@csrf_exempt
def register_people(request):
    try:
        # TODO : CHECK IF THE SCHOOL ADMIN IS LOGIN
        if request.method == 'POST':
            
            school_user = models.School.objects.filter(email_address=request.user.username).first()
            if not school_user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            
            role = request.POST.get('role')
            school_id = request.POST.get('school_id')
            employee_id = request.POST.get('employee_id')
            first_name = request.POST.get('first_name')
            middle_name = request.POST.get('middle_name')
            last_name = request.POST.get('last_name')
            email_address = request.POST.get('email_address')
            position = request.POST.get('position')
            job_started = request.POST.get('job_started')
            grade_level = request.POST.get('grade_level')
            department = request.POST.get('department')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                return JsonResponse({'status': 'error', 'message': 'Passwords do not match'}, status=400)
            
            if employee_id in models.People.objects.values_list('employee_id', flat=True):
                return JsonResponse({'status': 'error', 'message': 'Employee ID already exists'}, status=400)

            if not my_utils.parse_date_string(job_started):
                return JsonResponse({'status': 'error', 'message': 'Invalid date format', 'example': 'August 20, 2024'}, status=400)
                    
            people = People.objects.create(
                role=role,
                school_id=school_id,
                employee_id=employee_id,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                email_address=email_address,
                position=position,
                grade_level=grade_level,
                department=department,
                password=password,  # Storing plain password temporarily
            )
            
            people.action_id = str(uuid4())
            people.school_id = school_user.school_id
            people.fullname = f'{people.first_name} {people.middle_name} {people.last_name}'
            job_started_date = my_utils.parse_date_string(job_started)
            people.job_started = job_started_date
            people.is_accepted = True
            people.is_verified = True
            
            people.save()

            user = User.objects.create(
                username=employee_id,
                password=make_password(password)
            )

            return JsonResponse({'status': 'success', 'message': 'Faculty record created successfully' }, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Something went wrong : {e}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def add_people_by_school(request):
    try:
        if request.method == 'POST':
            
            school_user = models.School.objects.filter(email_address=request.user.username).first()
            if not school_user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            employee_id = request.POST.get('employee_id')
            if not employee_id:
                return JsonResponse({
                    'message' : 'Please provide employee_id',
                }, status=400)
            
            people = models.People.objects.filter(employee_id=employee_id).first()
            if not people:
                return JsonResponse({
                    'message' : 'Pople not found',
                }, status=400)
            

            people.is_accepted = True
            people.action_id = str(uuid4())
            people.save()
            
            user = User.objects.create(
                username=people.employee_id,
                password=make_password(people.password),
            )
            
            
            Thread(target=my_utils.send_account_info_email, args=(
                people.email_address, people.employee_id, people.password , 'registered-email.html' , settings.EMAIL_HOST_USER, f'{people.role} Registration'
                )).start()
            
            return JsonResponse({
                'message' : 'People verified successfully',
            }, status=200)
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def login_school(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('employee_id')
            password = request.POST.get('password')
            remember_me = request.POST.get('remember_me', False)
            
            if not email or not password:
                return JsonResponse({
                    'message' : 'Please provide school_id and password',
                    }, status=400)
            
            user = models.School.objects.filter(email_address=email, password=password).first()
            if not user:
                return JsonResponse({
                    'message' : 'Invalid school_id or password',
                    }, status=400)
            
            
            # if not user.is_verified:
            #     return JsonResponse({
            #         'message' : 'School not verified',
            #         }, status=400)
            
            # if not user.is_accepted:
            #     return JsonResponse({
            #         'message' : 'School not accepted, Wait for admin approval',
            #         }, status=400)
            
            
            
            user_authenticated = authenticate(request, username=email, password=password)
            if not user_authenticated:
                return JsonResponse({
                    'message' : 'Invalid school_id or password',
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
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def get_school_information(request):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(email_address=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            return JsonResponse({
                'school' : user.get_school_information()
            },status=200)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

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


@csrf_exempt
def get_all_school_faculty(request):
    try:
        if request.method == 'GET':
            
            user = models.School.objects.filter(email_address=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            people = models.People.objects.filter(is_accepted = True, school_id=user.school_id).order_by('-created_at')
            people_informations = [person.get_information() for person in people]
            people_informations.append(user.get_school_information())
            return JsonResponse({
                'people' : people_informations
            },status=200)
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400)


@csrf_exempt
def get_number_of_school_faculty(request):
    try:
        if request.method == 'GET':

            user = models.School.objects.filter(email_address=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)

            people = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role="Teacher")

            return JsonResponse({
                'number_of_school_faculty' : len(people)
            },status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400)


@csrf_exempt
def get_number_of_school_faculty_evaluated(request):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(email_address=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)

            people = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role="Teacher", is_evaluated=True)

            return JsonResponse({
                'number_of_school_faculty_evaluated' : len(people)
            },status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400) 


@csrf_exempt
def get_number_of_school_faculty_not_evaluated(request):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(email_address=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)

            people = models.People.objects.filter(is_accepted = True, school_id=user.school_id, role="Teacher", is_evaluated=False)

            return JsonResponse({
                'number_of_school_faculty_evaluated' : len(people)
            },status=200)

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400) 
    
    

@csrf_exempt
def search_school_faculty(request):
    try:
        if request.method == 'POST':
            query = request.POST.get('query')
            
            if not query:
                return JsonResponse({
                    'message' : 'Please provide query',
                    }, status=400)
            
            user = models.School.objects.filter(email_address=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            people = models.People.objects.filter(is_accepted = True, fullname__icontains=query , school_id=user.school_id).all()
            
            people_information = [person.get_information() for person in people]
            
            return JsonResponse({
                'people' : people_information
            },status=200)
            
            
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400)


@csrf_exempt
def get_search_school_faculty_for_mentioning(request):
    try:
        if request.method == 'POST':
            query = request.POST.get('query')

            if not query:
                return JsonResponse({
                    'message' : 'Please provide query',
                    }, status=400)

            user = models.School.objects.filter(email_address=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
                
            
            search_people = models.People.objects.filter(is_accepted = True, school_id=user.school_id, fullname__icontains=query) # Search by name
            if not search_people:
                return JsonResponse({
                    'people' : [],
                },status=200)
            
            return JsonResponse({
                'people' : [person.get_name_and_action_id() for person in search_people],
            },status=200)
                

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Something went wrong : {e}'
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request method'
    },status=400) 


@csrf_exempt
def school_get_all_teacher_tenure(request):
    try:
        
        if request.method == 'GET':
            user = models.School.objects.filter(email_address=request.user.username, role='Evaluator').first()
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
                '0-3 years': tenure_counts['0-3 years'],
                '3-5 years': tenure_counts['3-5 years'],
                '5+ years': tenure_counts['5+ years']
            }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def school_get_teacher_recommendations(request):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(email_address=request.user.username).first()
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
            
            number_of_promotion = number_of_promotion / teachers.count()
            number_of_termination = number_of_termination / teachers.count()
            number_of_retention = number_of_retention / teachers.count()
            
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
def school_get_annual_ratings(request):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(email_address=request.user.username).first()
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
                if ipcrf_1:
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
                            'total_score' : 0,
                        })
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
    }, status=400)


@csrf_exempt
def school_get_performance_true_year(request):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(email_address=request.user.username).first()
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
def reject_people_by_school(request):
    try:
        if request.method == 'POST':
            
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            employee_id = request.POST.get('employee_id')
            reason = request.POST.get('reason')
            if not employee_id:
                return JsonResponse({
                    'message' : 'employee_id is required',
                }, status=400)
                
            if not reason:
                return JsonResponse({
                    'message' : 'Reason is required',
                    'reason' : reason
                }, status=400)
            
            rejected_pople = models.People.objects.filter(employee_id=employee_id , school_id=user.school_id).first()
            if not rejected_pople:
                return JsonResponse({
                    'message' : 'People not found',
                }, status=400)
            
            role = rejected_pople.role 
            rejected_pople.is_accepted = False
            rejected_pople.is_declined = True
            rejected_pople.save()
            peoples = models.People.objects.filter(is_accepted=True , school_id=user.school_id).order_by('-created_at')
            
            Thread(target=my_utils.send_declined_reason, args=(
                rejected_pople.email_address, reason  , 'email_declined_teacher.html' , settings.EMAIL_HOST_USER, f'{role} Declined', request
                )).start()
            
            return JsonResponse({
                'message' : 'People rejected successfully',
                'peoples' : [people.get_information() for people in peoples],
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 




@csrf_exempt
def create_rpms_folder(request):
    try:
        if request.method == 'POST':
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            folder_name = request.POST.get('folder_name')
            rpms_folder_school_year = request.POST.get('school_year')
            position_rpms = request.POST.get('position_rpms') # (Proficient and Highly Proficient)
            background_color = request.POST.get('background_color')
            color = request.POST.get('color')
            
            
            if not folder_name:
                return JsonResponse({
                    'message' : 'Folder name is required',
                    'folder_name' : folder_name,
                }, status=400)
                        
            if not background_color:
                return JsonResponse({
                    'message' : 'Background color is required',
                    'background_color' : background_color,
                }, status=400)
            
            if not color:
                return JsonResponse({
                    'message' : 'Color is required',
                    'color' : color,
                }, status=400)
            
            if not rpms_folder_school_year:
                return JsonResponse({
                    'message' : 'School year is required',
                    'school_year' : rpms_folder_school_year,
                }, status=400)
            
            if not position_rpms:
                return JsonResponse({
                    'message' : 'Position RPMS is required',
                    'position_rpms' : position_rpms,
                }, status=400)
            
            if position_rpms not in ['Proficient', 'Highly Proficient']:
                return JsonResponse({
                    'message' : 'Position RPMS must be Proficient or Highly Proficient',
                    'position_rpms' : position_rpms,
                }, status=400)

            if models.RPMSFolder.objects.filter(is_for_teacher_proficient=True if position_rpms == 'Proficient' else False, rpms_folder_school_year=rpms_folder_school_year).exists():
                return JsonResponse({
                    'message' : 'RPMS folder already exists',
                    'rpms_folder_school_year' : rpms_folder_school_year,
                }, status=400)
            
            rpms_folder_id = str(uuid4())
            
            rpms_folder = models.RPMSFolder.objects.create(
                rpms_folder_name = folder_name,
                rpms_folder_school_year = rpms_folder_school_year,
                rpms_folder_color = color,
                rpms_folder_background_color = background_color,
                school_id = user.school_id
            )
            rpms_folder.rpms_folder_id = rpms_folder_id
            
            rpms_folder.is_for_teacher_proficient = True if position_rpms == 'Proficient' else False
            
            rpms_folder.save()

            # Create a rpms_classwork folder when the folder is created
            if position_rpms == 'Proficient':
                my_utils.create_rpms_class_works_for_proficient(rpms_folder_id=rpms_folder_id , school_id=user.school_id)
            elif position_rpms == 'Highly Proficient':
                my_utils.create_rpms_class_works_for_highly_proficient(rpms_folder_id=rpms_folder_id, school_id=user.school_id)
            
            return JsonResponse({
                'message' : 'RPMS folder created successfully',
                'rpms_name' : rpms_folder.rpms_folder_name,
                'rpms_school_year' : rpms_folder.rpms_folder_school_year,
            }, status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_rpms_folder_by_id(request):
    try:
        if request.method == 'POST':
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
             
            rpms_folder_id = request.POST.get('rpms_folder_id')
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'RPMS folder id is required',
                }, status=400)

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at').first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS folder not found',
                }, status=400)
            
            return JsonResponse({
                'rpms_folder' : rpms_folder.get_rpms_folder_information()
            }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def update_rpms_folder_background(request):
    try:
        if request.method == 'POST':
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
              
            rpms_folder_id = request.POST.get('rpms_folder_id')
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'RPMS folder id is required',
                }, status=400)

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at').first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS folder not found',
                }, status=400)

            background_image = request.FILES.get('background_image')
            if not background_image:
                return JsonResponse({
                    'message' : 'Background image is required',
                }, status=400)

            rpms_folder.background_image = background_image
            rpms_folder.save()
            
            return JsonResponse({
                'message' : 'RPMS folder background updated successfully',
            }, status=200)
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)




@csrf_exempt
def get_all_rpms_folders(request, type_proficient : str):
    try:
        if request.method == 'GET':
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            if type_proficient not in ['proficient', 'highly_proficient']:
                return JsonResponse({
                    'message' : 'Type proficient is required in "admin/forms/rpms/folders/<str:type_proficient>/" [ "proficient" , "highly_proficient" ]',
                    }, status=400)
                
            rpms_folders = models.RPMSFolder.objects.filter( school_id=user.school_id, is_for_teacher_proficient=True if type_proficient == 'proficient' else False).order_by('-created_at')
            
            return JsonResponse({
                'rpms_folders' : [
                    rpms_folder.get_rpms_folder_information() for rpms_folder in rpms_folders
                ]
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_rpms_classworks(request):
    try:
        if request.method == 'POST':
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
                
            
            rpms_folder_id = request.POST.get('rpms_folder_id')
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'RPMS folder id is required',
                }, status=400)

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at').first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS folder not found',
                }, status=400)
                
            rpms_classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at')
            
            
            return JsonResponse({
                'message' : 'RPMS classworks found successfully',
                'rpms_classworks' : [rpms_classwork.get_rpms_classwork_information() for rpms_classwork in rpms_classworks],
            }, status=200)
                
                
                
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    


@csrf_exempt
def get_rpms_classwork_by_id(request):
    try:
        if request.method == 'POST':
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
                
            
            rpms_classwork_id = request.POST.get('rpms_classwork_id')
            if not rpms_classwork_id:
                return JsonResponse({
                    'message' : 'RPMS classwork id is required',
                }, status=400)

            rpms_classwork = models.RPMSClassWork.objects.filter(rpms_classwork_id=rpms_classwork_id).order_by('-created_at').first()
            if not rpms_classwork:
                return JsonResponse({
                    'message' : 'RPMS classwork not found',
                }, status=400)
                
            return JsonResponse({
                'message' : 'RPMS classwork found successfully',
                'rpms_classwork' : rpms_classwork.get_rpms_classwork_information(),
            }, status=200)
                
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 






