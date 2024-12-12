
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import People
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.db.models.functions import ExtractYear
from django.db.models import Count
 
from django.conf import settings
import os


from . import models, my_utils , forms_text


import secrets
import string
from itertools import groupby
from uuid import uuid4
from threading import Thread
import json



@csrf_exempt
def get_school_year_kra(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
            
            if not user:
                user = models.School.objects.filter(email_address=request.user.username).first()
                if not user:
                    return JsonResponse({
                        "message": "User not found",
                    }, status=404)

            rmps_folders = models.RPMSFolder.objects.filter(school_id=user.school_id).order_by('-created_at')
            school_years = {
                'proficient': [],
                'highly_proficient': []
            }
            for rmps_folder in rmps_folders:
                if rmps_folder.is_for_teacher_proficient:
                    if rmps_folder.rpms_folder_school_year not in school_years['proficient']:
                        school_years['proficient'].append(rmps_folder.rpms_folder_school_year)
                else:
                    if rmps_folder.rpms_folder_school_year not in school_years['highly_proficient']:
                        school_years['highly_proficient'].append(rmps_folder.rpms_folder_school_year)
            
            return JsonResponse({
                "school_years": school_years,
            }, status=200)
            
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)


@csrf_exempt
def get_school_year_cot(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()

            if not user:
                user = models.School.objects.filter(email_address=request.user.username).first()
                if not user:
                    return JsonResponse({
                        "message": "User not found",
                    }, status=404)
                    
            cots = models.COTForm.objects.filter(school_id=user.school_id).order_by('-created_at')
            school_years = {
                'proficient': [],
                'highly_proficient': []
            }
            for cot in cots:
                if cot.is_for_teacher_proficient:
                    if cot.school_year not in school_years['proficient']:
                        school_years['proficient'].append(cot.school_year)
                else:
                    if cot.school_year not in school_years['highly_proficient']:
                        school_years['highly_proficient'].append(cot.school_year) 
            
            return JsonResponse({
                "school_years": school_years,
            }, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)



@csrf_exempt
def get_school_year_ipcrf(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
            if not user:
                user = models.School.objects.filter(email_address=request.user.username).first()
                if not user:
                    return JsonResponse({
                        "message": "User not found",
                    }, status=404)

            ipcrfs = models.IPCRFForm.objects.filter(school_id=user.school_id , form_type="PART 1").order_by('-created_at')
            school_years = {
                'proficient': [],
                'highly_proficient': []
            }
            for ipcrf in ipcrfs:
                if ipcrf.is_for_teacher_proficient:
                    if ipcrf.school_year not in school_years['proficient']:
                        school_years['proficient'].append(ipcrf.school_year)
                else:
                    if ipcrf.school_year not in school_years['highly_proficient']:
                        school_years['highly_proficient'].append(ipcrf.school_year)
            
            return JsonResponse({
                "school_years": school_years,
            }, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400) 




@csrf_exempt
def get_school_year_ipcrf_all(request):
    try:
        if request.method == "GET": 

            ipcrfs = models.IPCRFForm.objects.filter(form_type="PART 1").order_by('-created_at')
            school_years = {
                'proficient': [],
                'highly_proficient': []
            }
            for ipcrf in ipcrfs:
                if ipcrf.is_for_teacher_proficient:
                    if ipcrf.school_year not in school_years['proficient']:
                        school_years['proficient'].append(ipcrf.school_year)
                else:
                    if ipcrf.school_year not in school_years['highly_proficient']:
                        school_years['highly_proficient'].append(ipcrf.school_year)
            
            return JsonResponse({
                "school_years": school_years,
            }, status=200)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400) 





@csrf_exempt
def react_post(request):
    try:
        if request.method == "POST":
            
            user_type = "People"
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
            if not user:
                user_type = "School"
                user = models.School.objects.filter(email_address=request.user.username).first()
                if not user:
                    return JsonResponse({"status": "error", "message": "User not found"}, status=404)
            
            
            post_id = request.POST.get('post_id')
            if not post_id:
                return JsonResponse({"status": "error", "message": "Post ID is required"}, status=400)
            
            liked = request.POST.get('liked')
            if not liked:
                return JsonResponse({"status": "error", "message": "Liked is required"}, status=400)
            
            post = models.Post.objects.filter(post_id=post_id).first()
            if not post:
                return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
            """
                liked = [
                    action_id,
                    action_id,
                ]
            """
            if liked == "true":
                if user.action_id not in post.liked:
                    post.liked.append(user.action_id) 
                    # post.add_notification(user.action_id, "liked", user.fullname if user_type == "People" else user.school_name)
                    
                    school = models.School.objects.filter(school_id=user.school_id).first()
                    if school:
                        post.add_notification(school.action_id, "liked", user.fullname if user_type == "People" else user.school_name)
            else:
                if user.action_id in post.liked:
                    post.liked.remove(user.action_id)
                
            
            
            post.save()
            
            return JsonResponse({"status": "success", "message": "Post updated successfully"}, status=200)
    
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)




@csrf_exempt
def comment_post(request):
    try:
        if request.method == "POST":

            user_type = "People"
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
            if not user:
                user_type = "School"
                user = models.School.objects.filter(email_address=request.user.username).first()
                if not user:
                    return JsonResponse({"status": "error", "message": "User not found"}, status=404)


            post_id = request.POST.get('post_id')
            if not post_id:
                return JsonResponse({"status": "error", "message": "Post ID is required"}, status=400)
            
            comment = request.POST.get('comment')
            if not comment:
                return JsonResponse({"status": "error", "message": "Comment is required"}, status=400)
            
            
            post = models.Post.objects.filter(post_id=post_id).first()
            if not post:
                return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
            
            
            replied_to = request.POST.get('replied_to' , None) # Action id of the user responded
            
            
            comment_id = str(uuid4())
            comment = models.Comment.objects.create( 
                content=comment, 
                comment_id=comment_id, 
                comment_owner = user.action_id,
                post_id = post_id,
            )
            
            if replied_to:
                replied_people = models.People.objects.filter(is_deactivated = False, action_id=replied_to).first()
                if replied_people :
                    comment.replied_to = replied_to
                    comment.add_notification(replied_to, "replied", user.fullname if user_type == "People" else user.school_name)
            
            comment.save()
            school = models.School.objects.filter(school_id=user.school_id).first()
            if school and user_type == "People":
                post.add_notification(school.action_id, "commented", user.fullname if user_type == "People" else user.school_name)
            
            return JsonResponse({"status": "success", "message": "Comment added successfully"}, status=200)
            
            
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)



@csrf_exempt
def get_faculty_school_details(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
            if not user: 
                return JsonResponse({"status": "error", "message": "User not found"}, status=404)
            school = models.School.objects.filter(school_id=user.school_id).first()
            return JsonResponse( school.get_school_information() if school else {} , status=200) 
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)





@csrf_exempt
def react_comment(request):
    try:
        if request.method == "POST":
            
            user_type = "People"
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
            if not user:
                user_type = "School"
                user = models.School.objects.filter(email_address=request.user.username).first()
                if not user:
                    return JsonResponse({"status": "error", "message": "User not found"}, status=404)
            
            
            comment_id = request.POST.get('comment_id')
            if not comment_id:
                return JsonResponse({"status": "error", "message": "comment_id is required"}, status=400)
            
            liked = request.POST.get('liked')
            if not liked:
                return JsonResponse({"status": "error", "message": "Liked is required"}, status=400)
            
            comment = models.Comment.objects.filter(comment_id=comment_id).first()
            if not comment:
                return JsonResponse({"status": "error", "message": "Comment not found"}, status=404)
            
            post = models.Post.objects.filter(post_id=comment.post_id).first()
            if not post:
                return JsonResponse({"status": "error", "message": "Post not found"}, status=404)
            
            """
                liked = [
                    action_id,
                    action_id,
                ]
            """
            if liked == "true":
                if user.action_id not in comment.liked:
                    comment.liked.append(user.action_id) 
                    # post.add_notification(user.action_id, "liked", user.fullname if user_type == "People" else user.school_name)
                    
                    reacted_people = models.People.objects.filter(is_deactivated = False, action_id=comment.comment_owner).first()
                    if reacted_people:
                        comment.add_notification(reacted_people.action_id, "liked", user.fullname if user_type == "People" else user.school_name)
            else:
                if user.action_id in comment.liked:
                    comment.liked.remove(user.action_id)
                
            
            
            comment.save()
            
            return JsonResponse({"status": "success", "message": "Post updated successfully"}, status=200)
    
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)


