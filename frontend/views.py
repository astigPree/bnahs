from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth.models import User

from backend import models


# Create your views here.

@csrf_exempt
def verify_school_people(request, token):
    
    try:
        
        if not token:
            return JsonResponse({
                'message' : 'Please provide token',
                }, status=400)
        
        verification = models.VerificationLink.objects.filter(verification_link=token).first()
        if not verification:
            return JsonResponse({
                'message' : 'Invalid token',
                'token' : token
                }, status=400)
        
        if verification.is_expired():
            verification.delete()
            return redirect("http://www.deped-performance-evaluation-system3211.online/expired%20token/token_expired.html")
        
        
        user = models.School.objects.filter(email_address=verification.email).first()
        if not user:
            user = models.People.objects.filter(email_address=verification.email).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400) 
        
        user.is_verified = True
        user.save()
        verification.delete()
        
        # return JsonResponse({
        #     'message' : 'School verified successfully, Wait for admin approval',
        #     }, status=200)
        
        return redirect("http://www.deped-performance-evaluation-system3211.online/")
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        

@csrf_exempt
def verify_changes_password(request, token):
    try:

        if not token:
            return JsonResponse({
                'message' : 'Please provide token',
                }, status=400)

        verification = models.VerificationLink.objects.filter(verification_link=token).first()
        if not verification:
            return JsonResponse({
                'message' : 'Invalid token',
                'token' : token
                }, status=400)

        if verification.is_expired():
            verification.delete()
            return JsonResponse({
                'message' : 'Token expired',
                }, status=400)
        
        password = verification.data.get('password', None)
        if not password:
            return JsonResponse({
                'message' : 'Please provide password',
                'data' : verification.data
                }, status=400)
        
        user_type = verification.data.get('user_type', None)
        if not user_type:
            return JsonResponse({
                'message' : 'Please provide user type',
                'data' : verification.data
                }, status=400)
            
        if user_type == 'school':
            user = models.School.objects.filter(email_address=verification.email).first()
        elif user_type == 'people':
            user = models.People.objects.filter(email_address=verification.email).first()
        
        if not user:
            return JsonResponse({
                'message' : 'User not found',
                }, status=400)
        
        # Re-authenticate the user with the new credentials
        if user_type == 'school':
            old_based_user = User.objects.get(username=user.email_address)
        elif user_type == 'people':
            old_based_user = User.objects.get(username=user.employee_id)
            
        
        old_based_user.set_password(password)  
        old_based_user.save()
        user.password = password
        user.confirm_password = password
        user.save()
        verification.delete()
        
        return redirect("http://www.deped-performance-evaluation-system3211.online/")

    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    

