
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


# Create your views here.

# ================================= General Views =============================== #

@csrf_exempt
def create_main_admin(request):
    """
        This function only create a a Main Admin, so it must be activated once
    """
    try:
        user = models.MainAdmin.objects.all().first()
        
        
        if user:
            return JsonResponse({
                'message' : 'Main admin already created',
                'employee_id': user.username,
                'password' : user.password
            }, status=400)
            
        admin = models.MainAdmin.objects.create(
            username = 'admin',
            password = 'admin',
        )
        
        user = User.objects.create(
            username=admin.username,
            password=make_password(admin.password),
        )
        
        return JsonResponse({
            'message' : 'Main admin created',
            'employee_id': 'admin',
            'password' : 'admin'
        }, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : 'Something went wrong',
            }, status=500)
    


@csrf_exempt
def get_feeds(request):
    """
    This function is used to get the People feeds.
    """
    
    try:
        if request.method == 'GET':  
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            
            
            feeds = {}
            posts = models.Post.objects.filter(post_owner=user.school_action_id).order_by('-created_at')
            for post in posts:
                comments = models.Comment.objects.filter(post_id=post.post_id).order_by('-created_at')
                feeds[post.post_id] = {
                    "post" : post.get_post(action_id=user.action_id),
                    "comments" : [comment.get_comment() for comment in comments]
                }
            
            return JsonResponse({
                'feeds' : feeds
            },status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'message' : 'Something went wrong',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_notifications(request):
    """
        This function is used to get the People notifications.
    """
    
    try:
        if request.method == 'GET':  
            
            user = models.People.objects.filter(username=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            notifications = []
            
            comments = models.Comment.objects.filter(user_id=user.id).order_by('-created_at')
            for comment in comments:
                if comment.is_seen(user.action_id)[0]:
                    notifications.append(comment.get_comment())
            
            
            
            return JsonResponse({
                'notifications' : notifications
            },status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'message' : 'Something went wrong',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    
    
    
@csrf_exempt
def people_update_education(request ):
    if request.method == 'POST':

        try:
            # Update educations if have
            educations = request.POST.get('educations')
            
            if not educations:
                return JsonResponse({
                    'message' : 'Please provide educations',
                }, status=400)
                
            if educations:
                user = models.People.objects.filter(employee_id=request.user.username).first()
                if not user:
                    return JsonResponse({
                        'message' : 'User not found',
                    }, status=400)
                
                user.update_educations(educations)
                return JsonResponse({
                    'message' : 'Educations updated successfully',
                }, status=200)
                
                
        except Exception as e:
            return JsonResponse({
                'message' : f'Something went wrong : {e}',
                }, status=500)
    
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def people_update_profile(request ):
    if request.method == 'POST':

        user = models.People.objects.filter(employee_id=request.user.username).first()
        based_user = User.objects.filter(username=request.user.username).first()
        
        if not user:
            return JsonResponse({
                'message' : 'User not found',
            }, status=400)
        
        
        try:
            # Update profile if have
            has_changed = False
            firstname = request.POST.get('firstname')
            
            if firstname:
                user.first_name = firstname
                has_changed = True
            
            middlename = request.POST.get('middlename')
            if middlename:
                user.middle_name = middlename
                has_changed = True
            
            lastname = request.POST.get('lastname')
            if lastname:
                user.last_name = lastname
                has_changed = True
            
            jobtitle = request.POST.get('jobtitle')
            if jobtitle:
                user.position = jobtitle
                has_changed = True
            
            department = request.POST.get('department')
            if department:
                user.department = department
                has_changed = True
                
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if password and password == confirm_password:
                if based_user:
                    pass
                    
                    # TODO : Change password
                has_changed = True    
                
            
            
            if has_changed:
                user.save()
                return JsonResponse({
                    'message' : 'Profile updated successfully',
                }, status=200)
            
            return JsonResponse({
                'message' : 'No changes made',
            }, status=200)
            
                
        except Exception as e:
            return JsonResponse({
                'message' : f'Something went wrong : {e}',
                }, status=500)
    
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def people_logout(request ):
    try:
        if request.method == 'POST':
            logout(request)
            return JsonResponse({
                'message' : 'Logout successful'
                }, status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_people_all_rpms_folders(request):
    try:
        if request.method == 'POST':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                

            rpms_folders = models.RPMSFolder.objects.all()
            if not rpms_folders:
                return JsonResponse({
                    'message' : 'No rpms folders found',
                }, status=400)
            
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
def get_people_rpms_classworks(request):
    try:
        if request.method == 'POST':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                
            
            rpms_folder_id = request.POST.get('rpms_folder_id')
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'RPMS folder id is required',
                }, status=400)

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS folder not found',
                }, status=400)
                
            rpms_classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpms_folder_id)
            if not rpms_classworks:
                return JsonResponse({
                    'message' : 'RPMS classworks not found',
                }, status=400)
            
            
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
def register_school(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        school_id = request.POST.get('school_id')
        school_name = request.POST.get('school_name')
        school_address = request.POST.get('school_address')
        school_type = request.POST.get('school_type')
        contact_number = request.POST.get('contact_number')
        email_address = request.POST.get('email_address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        school_logo = request.FILES.get('school_logo')

        if password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match'}, status=400)

        school = models.School.objects.create(
            name=name,
            school_id=school_id,
            school_name=school_name,
            school_address=school_address,
            school_type=school_type,
            contact_number=contact_number,
            email_address=email_address,
            password=password,
            school_logo=school_logo
        )
        
        school.action_id = str(uuid4())
        school.save()
        
        verification = models.VerificationLink.generate_link(email_address)
        
        # verification_code , template , masbate_locker_email , subject
        Thread(target=my_utils.send_verification_email, args=(
            email_address, verification , 'verification_link.html', settings.EMAIL_HOST_USER, 'School Registration'
        )).start()
        

        return JsonResponse({
            'status': 'success',
            'message': 'Check your email for verification link in order to activate your account',
        },status=200)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# ================================= Admin Views ============================== # 
@csrf_exempt
def login_admin(request):
    try:
        if request.method == 'POST':
            employee_id = request.POST.get('employee_id')
            password = request.POST.get('password')
            
            if not employee_id or not password:
                return JsonResponse({
                    'message' : 'Please provide employee_id and password',
                    }, status=400)
            
            user = models.MainAdmin.objects.filter(username=employee_id, password=password).first()
            if not user:
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
                'message' : 'Login successful',
                }, status=200)
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def add_school(request):
    try:
        if request.method == 'POST':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            school_id = request.POST.get('school_id')
            if not school_id:
                return JsonResponse({
                    'message' : 'Please provide school_id',
                }, status=400)
            
            school = models.School.objects.filter(school_id=school_id).first()
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            

            school.is_accepted = True
            school.action_id = str(uuid4())
            school.save()
            
            user = User.objects.create(
                username=school.email_address,
                password=make_password(school.password),
            )
            
            
            Thread(target=my_utils.send_account_info_email, args=(
                school.email_address, school.email_address, school.password , 'account.html' , settings.EMAIL_HOST_USER, 'School Registration'
                )).start()
            
            return JsonResponse({
                'message' : 'School verified successfully',
            }, status=200)
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_school_inbox(request):
    try:
        if request.method == 'GET':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            school = models.School.objects.all().order_by('-created_at')
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            
            return JsonResponse({
                'school' : [school.get_school_information() for school in school],
            }, status=200)
            
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_all_schools(request):
    try:
        if request.method == 'GET':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            schools = models.School.objects.all().order_by('-created_at')
            if not schools:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            
            return JsonResponse({
                'schools' : [school.get_school_information() for school in schools],
            }, status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_search_schools(request):
    try:
        if request.method == 'POST':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            query = request.POST.get('query')
            if not query:
                return JsonResponse({
                    'message' : 'Please provide query',
                }, status=400)
            
            schools = models.School.objects.filter(school_name__icontains=query)
            if not schools:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            
            return JsonResponse({
                'schools' : [school.get_school_information() for school in schools],
            }, status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

@csrf_exempt
def get_search_schools_by_location(request):
    try:
        if request.method == 'POST':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)

            query = request.POST.get('query')
            if not query:
                return JsonResponse({
                    'message' : 'Please provide query',
                }, status=400)

            schools = models.School.objects.filter(school_address__icontains=query)
            if not schools:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)

            return JsonResponse({
                'schools' : [school.get_school_information() for school in schools],
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

    

@csrf_exempt
def get_total_number_of_schools(request):
    try:
        if request.method == 'GET':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)

            schools = models.School.objects.all()

            return JsonResponse({
                'total_schools' : schools.count() if schools else 0,
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 
    

@csrf_exempt
def get_total_number_of_teachers_in_all_school(request):
    try:
        if request.method == 'GET':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)

            teachers = models.People.objects.filter(role='Teacher')
            
            return JsonResponse({
                'total_teachers' :  teachers.count() if teachers else 0,
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def number_of_evaluation_conducted(request):
    # TODO : DOUBLE CHECK IF IM CORRECT ON THE DATA 
    try:
        if request.method == 'GET':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            teachers = models.People.objects.filter(role='Teacher' , is_evaluated=True)
            
            return JsonResponse({
                'total_evaluation_conducted' : teachers.count() if teachers else 0,
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
            

@csrf_exempt
def number_of_pending_evaluation(request):
    try:
        if request.method == 'GET':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                
            teachers = models.People.objects.filter(role='Teacher', is_evaluated=False)

            return JsonResponse({
                'total_pending_evaluation' : teachers.count() if teachers else 0,
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def evaluation_submission_rate(request):
    return JsonResponse({
        'message' : 'Not yet implemented',
    }, status=400)
    
@csrf_exempt
def all_teacher_recommendations(request):
    return JsonResponse({
        'message' : 'Not yet implemented',
    }, status=400)


@csrf_exempt
def all_teacher_tenure(request):
    return JsonResponse({
        'message' : 'Not yet implemented',
    }, status=400)
    
    
@csrf_exempt
def distribution_ratings(request):
    return JsonResponse({
        'message' : 'Not yet implemented',
    }, status=400)


@csrf_exempt
def reject_school(request):
    try:
        if request.method == 'POST':
            
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            school_id = request.POST.get('school_id')
            if not school_id:
                return JsonResponse({
                    'message' : 'School id is required',
                }, status=400)
            
            rejected_school = models.School.objects.filter(id=school_id).first()
            if not rejected_school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
                
            rejected_school.is_accepted = False
            schools = models.School.objects.filter(is_accepted=True).order_by('-created_at')

            return JsonResponse({
                'message' : 'School rejected successfully',
                'schools' : [school.get_school_information() for school in schools],
            }, status=200)
            

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 


@csrf_exempt
def create_rating_sheet(request):
    try:
        if request.method == 'POST':

            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            content = request.POST.get('content')
            if not content:
                return JsonResponse({
                    'message' : 'Content is required',
                }, status=400)
            

            # TODO : WAIT FOR UPDATE IN IDENTIFICATION ID OF OBSERVER AND TEACHER
            # Checking if the data is exist before saving
            content : dict = json.loads(content)
            # Matatangap na data sa front end
            """
                {
                    "COT Type" : "Proficient", ! Used to identify what rating type of form
                    "Observer ID" : "Evaluator ID",
                    "Observer Name" : "Evaluator Name", ! Pwede blanko pagpasa
                    "Teacher Name" : "Evaluated Name", ! Pwede blanko pagpasa
                    "Teacher ID" : "Evaluated ID",
                    "Subject & Grade Level" : "Subject & Grade 7",
                    "Date : "September 05, 2023", 
                    "Quarter": "1st Quarter"
                }
            """
            cot_type = content['COT Type']
            observer = content['Observer ID']
            teacher_observed = content['Teacher ID']
            taught = content['Subject & Grade Level'] 
            date = content['Date']
            quarter = content['Quarter']
            
            # Check for evaluator
            search_observer = models.People.objects.filter(employee_id=observer, role='Evaluator').first()
            if not search_observer:
                return JsonResponse({
                    'message' : 'Observer not found',
                }, status=400)
            
            if cot_type == 'Proficient':
                if not my_utils.is_proficient_faculty(search_observer):
                    return JsonResponse({
                        'message' : 'Observer is not a proficient faculty',
                    }, status=400)
            elif cot_type == 'Highly Proficient':
                if not my_utils.is_highly_proficient_faculty(search_observer):
                    return JsonResponse({
                        'message' : 'Observer is not a highly proficient faculty',
                    }, status=400)
            else :
                return JsonResponse({
                    'message' : 'COT type not found',
                }, status=400)
            
            
            search_teacher = models.People.objects.filter(employee_id=teacher_observed , role='Teacher').first()
            if not search_teacher:
                return JsonResponse({
                    'message' : 'Teacher observed not found',
                }, status=400)
            
            
            school = models.School.objects.filter(school_id=search_observer.school_id).first()
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)
            
            
            my_utils.create_cot_form(
                school=school, 
                observer=search_observer, 
                teacher_observed=search_teacher, 
                subject=taught, 
                cot_date=date, 
                quarter=quarter
            )
            

            return JsonResponse({
                'message' : 'Rating sheet created successfully',
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
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
            
            
            folder_name = request.POST.get('folder_name')
            rpms_folder_school_year = request.POST.get('school_year')
            
            if not folder_name:
                return JsonResponse({
                    'message' : 'Folder name is required',
                }, status=400)
            
            
            if not rpms_folder_school_year:
                return JsonResponse({
                    'message' : 'School year is required',
                }, status=400)
            
            
            rpms_folder = models.RPMSFolder.objects.create(
                rpms_folder_name = folder_name,
                rpms_folder_school_year = rpms_folder_school_year
            )
            rpms_folder.rpms_folder_id = str(uuid4())
            rpms_folder.save()

            
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
def get_all_rpms_folders(request):
    try:
        if request.method == 'POST':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                

            rpms_folders = models.RPMSFolder.objects.all()
            
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
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                
            
            rpms_folder_id = request.POST.get('rpms_folder_id')
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'RPMS folder id is required',
                }, status=400)

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id).first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS folder not found',
                }, status=400)
                
            rpms_classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpms_folder_id)
            
            
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
def create_ipcrf_form(request):
    try:
        
        if request.method == 'POST':
            user = models.MainAdmin.objects.filter(username=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            if user.role != 'ADMIN':
                return JsonResponse({
                    'message' : 'User is not an admin',
                }, status=400)
                
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    
    
    
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
            
            error = "None"
            try:
                job_started_date = my_utils.parse_date_string(job_started)
                people.job_started = job_started_date
            except Exception as e:
                error = str(e)  # Log the error or handle it appropriately
            
            
            people.save()

            user = User.objects.create(
                username=employee_id,
                password=make_password(password)
            )

            return JsonResponse({'status': 'success', 'message': 'Faculty record created successfully' , 'error': error}, status=200)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Something went wrong : {e}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def login_school(request):
    try:
        if request.method == 'POST':
            email = request.POST.get('employee_id')
            password = request.POST.get('password')
            
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
                feeds[post.post_id] = {
                    "post" : post.get_post(),
                    "comments" : [comment.get_comment() for comment in comments]
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
            content_file = request.FILES.get('content_file')
            
            if not content:
                return JsonResponse({
                    'message' : 'Please provide content',
                    }, status=400)
            
            
            post = models.Post.objects.create(
                post_owner=user.action_id,
                content=content,
                content_file=content_file if content_file else ''
            )
            
            post.post_id = str(uuid4())
            post.save()
            
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
            
            user = models.School.objects.filter(school_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            people = models.People.objects.filter(school_id=user.school_id).all().order_by('-created_at')
            people_informations = [person.get_information() for person in people]
            
            return JsonResponse({
                'people' : people_informations.append(user.get_school_information())
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

            user = models.School.objects.filter(school_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)

            people = models.People.objects.filter(school_id=user.school_id, role="Teacher")

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
            user = models.School.objects.filter(school_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)

            people = models.People.objects.filter(school_id=user.school_id, role="Teacher", is_evaluated=True)

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
            user = models.School.objects.filter(school_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)

            people = models.People.objects.filter(school_id=user.school_id, role="Teacher", is_evaluated=False)

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
            
            user = models.School.objects.filter(school_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            people = models.People.objects.filter(fullname__icontains=query , school_id=user.school_id).all()
            
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

            user = models.School.objects.filter(school_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
                
            
            search_people = models.People.objects.filter(school_id=user.school_id, fullname__icontains=query) # Search by name
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








