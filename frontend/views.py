from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect

from backend import models


# Create your views here.

@csrf_exempt
def verify_school(request, token):
    
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
            return JsonResponse({
                'message' : 'Token expired',
                }, status=400)
        
        
        school = models.School.objects.filter(email_address=verification.email).first()
        if not school:
            return JsonResponse({
                'message' : 'School not found',
                }, status=400)
        
        school.is_verified = True
        school.save()
        verification.delete()
        
        # return JsonResponse({
        #     'message' : 'School verified successfully, Wait for admin approval',
        #     }, status=200)
        
        return redirect("https://www.youtube.com/")
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        



