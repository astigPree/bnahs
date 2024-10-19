
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import People
from django.contrib.auth import authenticate, login, logout


from . import models, my_utils


# Create your views here.

# ================================= General Views =============================== #
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

        return JsonResponse({
            'status': 'success',
            'message': 'Check your email for verification link in order to activate your account',
        })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# ================================= Admin Views ============================== # 


# ================================= School Views ============================== # 


@csrf_exempt
def register_teacher(request):
    try:
        # TODO : CHECK IF THE SCHOOL ADMIN IS LOGIN
        if request.method == 'POST':
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
                job_started=my_utils.parse_date_string(job_started),
                grade_level=grade_level,
                department=department,
                password=password,  # Storing plain password temporarily
            )

            user = User.objects.create(
                username=employee_id,
                password=make_password(password)
            )

            return JsonResponse({'status': 'success', 'message': 'User and People record created successfully'})

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Something went wrong : {e}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)



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
def teacher_dashboard(request ):
    """
    This function is used to render teacher home.
    """
    
    try:
        if request.method == 'GET':  
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            feeds = {
                
            }
            posts = models.Post.objects.all().order_by('-created_at')
            for post in posts:
                comments = models.Comment.objects.filter(post_id=post.id).order_by('-created_at')
                feeds[post.id] = {
                    "post" : post.get_post(),
                    "comments" : [comment.get_comment() for comment in comments]
                }
            
            return JsonResponse({
                'feeds' : feeds,
                'user' : user.get_information()
            },status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'message' : 'Something went wrong',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_evaluation(request ):
    pass


@csrf_exempt
def teacher_forms(request ):
    try:
        if request.method == 'GET': 
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
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
def teacher_report(request ):
    pass

@csrf_exempt
def teacher_profile(request ):
    if request.method == 'GET':
        try:
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            
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
        

    elif request.method == 'POST':

        try:
            educations = request.POST.get('educations')
            if not educations:
                return JsonResponse({
                    'message' : 'Please provide educations',
                }, status=400)
                
            
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
def teacher_logout(request ):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({
            'message' : 'Logout successful'
            }, status=200)

    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)





