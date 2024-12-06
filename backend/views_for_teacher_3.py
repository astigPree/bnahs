
from django.http import HttpResponse, JsonResponse 
from django.contrib.auth.models import User 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt    

from . import models, my_utils , my_utils_2
 


# ================================= Teacher Views =============================== #



@csrf_exempt
def teacher_download_report(request):
    try:
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            
            school = models.School.objects.filter(school_id=user.school_id).first()
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                }, status=400)

            buffer = my_utils_2.generate_report_by_teacher(school , user)
            if not buffer:
                return JsonResponse({
                    'message' : 'Report not found',
                    }, status=400) 
            return HttpResponse(buffer, content_type='application/pdf')
            
            
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
            
            school_year = request.GET.get('school_year', None)

            return JsonResponse( my_utils.get_kra_breakdown_of_a_teacher(employee_id=user.employee_id , school_year=school_year) , status=200)
    
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


 


