
from django.http import HttpResponse, JsonResponse 
from django.contrib.auth.models import User 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt    
from django.utils import timezone 

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
def teacher_private_comment(request):
    try:
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            attachment_id = request.POST.get('attachment_id')
            comment = request.POST.get('comment')
            if not attachment_id:
                return JsonResponse({
                    'message' : 'Attachment ID is required',
                }, status=400)
                
            if not comment:
                return JsonResponse({
                    'message' : 'Comment is required',
                }, status=400)
                
            attachment = models.RPMSAttachment.objects.filter(attachment_id=attachment_id).first()
            attachment.teacher_comments.append(
                        {
                            'comment' : comment, 
                            'date' : str(timezone.now()) , 
                            'role' : 'Teacher', 
                            'name' : user.fullname,
                            'image' : user.profile.url if user.profile else ''
                        }
                    )
            attachment.save()
            return JsonResponse({
                'message' : 'Comment added successfully',
                }, status=200)
            
                
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)

