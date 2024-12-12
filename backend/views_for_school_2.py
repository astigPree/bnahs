
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



@csrf_exempt
def school_summary(request):
    try:
        
        if request.method == "GET":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            teachers = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, role='Teacher')
            teacher_count = teachers.count()
            evaluated_teacher_count = teachers.filter(is_evaluated = True).count()
            un_evaluated_teacher_count = teachers.filter(is_evaluated = False).count()
            
            
            
            return JsonResponse({
                'teachers': [teacher.get_information() for teacher in teachers],
                'teacher_count' : teacher_count,
                'evaluated_teacher_count' : evaluated_teacher_count,
                'un_evaluated_teacher_count' : un_evaluated_teacher_count
            }, status=200)
            
            
                
                
                
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def school_summary_recommendations(request):
    try:
        
        if request.method == "POST":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id is required',
                    }, status=400)
            
            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)
            
            
            result = my_utils.get_recommendation_result_with_percentage(employee_id=teacher.employee_id)
            
            return JsonResponse({
                'message' : 'Recommendation result found successfully',
                'result' : result,
            }, status=200)

    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)




@csrf_exempt
def school_summary_performance(request):
    try:
        
        if request.method == "POST":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id is required',
                    }, status=400)

            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)
                
            
            result = my_utils.get_performance_by_years(employee_id=teacher.employee_id)
            
            return JsonResponse({
                'message' : 'Performance result found successfully',
                'result' : result,
            }, status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def school_summary_rpms(request):
    try:
        
        if request.method == "POST":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id is required',
                    }, status=400)

            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            school_year = request.POST.get('school_year', None)
            
            return JsonResponse( my_utils.get_kra_breakdown_of_a_teacher(employee_id=teacher.employee_id , school_year=school_year) , status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def school_get_kras_scores(request):
    try:
        
        if request.method == "GET":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            result_dict ={
                "kra" : [
                    "KRA 1",
                    "KRA 2",
                    "KRA 3" ,
                    "KRA 4" ,
                    "Plus Factor",
                    "Total Score"
                ],
                "averages" : [
                    
                ]
                
            } 

            teachers = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, role='Teacher')
            kra1 = 0.0
            kra2 = 0.0
            kra3 = 0.0
            kra4 = 0.0
            plus_factor = 0.0
            total_score = 0.0
            for teacher in teachers:
                result = my_utils.get_kra_breakdown_of_a_teacher(employee_id=teacher.employee_id)
                kra1 += result['averages'][0]
                kra2 += result['averages'][1]
                kra3 += result['averages'][2]
                kra4 += result['averages'][3]
                plus_factor += result['averages'][4]
                total_score += result['averages'][5]
            result_dict["averages"].append(kra1/len(teachers) if len(teachers) > 0 else 0.0)
            result_dict["averages"].append(kra2/len(teachers) if len(teachers) > 0 else 0.0)
            result_dict["averages"].append(kra3/len(teachers) if len(teachers) > 0 else 0.0)
            result_dict["averages"].append(kra4/len(teachers) if len(teachers) > 0 else 0.0)
            result_dict["averages"].append(plus_factor/len(teachers) if len(teachers) > 0 else 0.0)
            result_dict["averages"].append(total_score/len(teachers) if len(teachers) > 0 else 0.0)
            
            return JsonResponse( result_dict  , status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)




@csrf_exempt
def school_summary_swot(request):
    try:
        if request.method == "POST":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id is required',
                    }, status=400)

            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            strength = "The teacher has not been rated yet."
            weakness = "The teacher has not been rated yet."
            opportunity = "The teacher has not been rated yet."
            threat = "The teacher has not been rated yet."

            latest_cot = None
            cot_1 = models.COTForm.objects.filter(evaluated_id=teacher.employee_id, quarter="Quarter 1").order_by('-created_at').first()
            if cot_1:
                if cot_1.is_checked:
                    latest_cot = cot_1
            
            cot_2 = models.COTForm.objects.filter(evaluated_id=teacher.employee_id, quarter="Quarter 2").order_by('-created_at').first()
            if cot_2:
                if cot_2.is_checked:
                    latest_cot = cot_2
            
            cot_3 = models.COTForm.objects.filter(evaluated_id=teacher.employee_id, quarter="Quarter 3").order_by('-created_at').first()
            if cot_3:
                if cot_3.is_checked:
                    latest_cot = cot_3
            
            cot_4 = models.COTForm.objects.filter(evaluated_id=teacher.employee_id, quarter="Quarter 4").order_by('-created_at').first()
            if cot_4:
                if cot_4.is_checked:
                    latest_cot = cot_4
            error = "Wala namam"
            all_result = None
            if latest_cot:
                if not latest_cot.isAlreadyAIGenerated():
                    data = latest_cot.generatePromtTemplateNew() 
                    # while True:
                    #     strength = my_utils.generate_text(data['strengths'])
                    #     if strength:
                    #         if len(strength) < 500: 
                    #             break
                    # while True:       
                    
                    #     weakness = my_utils.generate_text(data['weaknesses'])
                    #     if weakness:
                    #         if len(weakness) < 500: 
                    #             break
                    # while True:
                    #     opportunity = my_utils.generate_text(data['opportunities'])
                    #     if opportunity:
                    #         if len(opportunity) < 500: 
                    #             break
                            
                    # while True: 
                    #     threat = my_utils.generate_text(data['threats'])
                    #     if threat:
                    #         if len(threat) < 500: 
                    #             break
                    # strength = my_utils.generate_text(data['strengths'])
                    # weakness = my_utils.generate_text(data['weaknesses'])
                    # opportunity = my_utils.generate_text(data['opportunities'])
                    # threat = my_utils.generate_text(data['threats'])
                    all_result = my_utils.generate_text_v2(data) 
                    strength = all_result.get('strengths_prompt', "The GPT is in currently working, Please try again.")
                    weakness = all_result.get('weaknesses_prompt', "The GPT is in currently working, Please try again.")
                    opportunity = all_result.get('opportunities_prompt', "The GPT is in currently working, Please try again.")
                    threat = all_result.get('threats_prompt', "The GPT is in currently working, Please try again.")
                    latest_cot.strengths_prompt = all_result.get('strengths_prompt', None)
                    latest_cot.weaknesses_prompt = all_result.get('weaknesses_prompt', None)
                    latest_cot.opportunities_prompt = all_result.get('opportunities_prompt', None)
                    latest_cot.threats_prompt = all_result.get('threats_prompt', None)
                    latest_cot.save()
                    error = all_result.get('error', None)
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
                'error' : error,
                'all_result' : all_result
            }, status=200)
            
            
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)



@csrf_exempt
def get_all_teachers_by_school(request):
    try:
        if request.method == "GET":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            teachers = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, role='Teacher').all()
            data = {
                "proficient" : [],
                "highly_proficient" : [],
            }
            
            for teacher in teachers:
                if my_utils.is_proficient_faculty(teacher):
                    data['proficient'].append(teacher.get_information())
                else:
                    data['highly_proficient'].append(teacher.get_information())
            return JsonResponse(data, status=200)
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)





@csrf_exempt
def get_school_report(request):
    try:
        if request.method == "GET":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
                
            
            buffer = my_utils.generate_report(user)
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
def get_all_teacher_by_status(request):
    try:
        if request.method == "GET":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            peoples = models.People.objects.filter(school_id=user.school_id).all()
            data = {
                "all" : [],
                "accepted" : [],
                "rejected" : [],
                "pending" : []
            }
            
            for people in peoples:
                if people.is_accepted:
                    data['accepted'].append(people.get_information())
                elif people.is_declined:
                    data['rejected'].append(people.get_information())
                elif not people.is_accepted and not people.is_declined:
                    data['pending'].append(people.get_information())
                    
                data['all'].append(people.get_information())
            
            return JsonResponse(data, status=200)

    
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)





@csrf_exempt
def teacher_generate_report_by_school(request):
    try:
        
        if request.method == "POST":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            school_year = request.POST.get('school_year', None)
             
            teachers = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, role='Teacher')
            
            main_data = []
            
            for teacher in teachers:
                    
                data = {
                    
                }
                
                data['job'] = teacher.get_job_years()
                data['recommendation'] = my_utils.get_recommendation_result_with_percentage(employee_id=teacher.employee_id)
                if school_year :
                    ipcrf = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id, form_type='PART 1', school_year=school_year).order_by('-created_at').first()
                else :
                    ipcrf = models.IPCRFForm.objects.filter(employee_id=teacher.employee_id, form_type='PART 1').order_by('-created_at').first()
                
                
                data['rating'] = ipcrf.get_information() if ipcrf else None
                data['performance_rating'] = my_utils.classify_ipcrf_score(ipcrf.evaluator_rating if ipcrf else 0.0)
                data['ranking'] = my_utils.recommend_rank(teacher=teacher , school_year=school_year)
                data['teacher'] = teacher.get_information()
                data['rater'] = None
                if ipcrf:
                    rater = models.People.objects.filter(employee_id=ipcrf.evaluator_id).first()
                    if rater:
                        data['rater'] = rater.get_information()
                
                main_data.append(data)
            
            return JsonResponse({
                'data': main_data
                },status=200)
            
    
    except Exception as e: 
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400 )








@csrf_exempt
def school_get_records_cot(request):
    try:
        if request.method == "POST":
            
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            
            data = {
                "hp_school_year" : [],
                "p_school_year" : [],
                "quarter" : [],
                "cot_taker" : [],
            }
            
            school_year = request.POST.get('school_year', None)
            if school_year:
                cots = models.COTForm.objects.filter(school_id=user.school_id , school_year=school_year).order_by('-created_at')
            else:
                cots = models.COTForm.objects.filter(school_id=user.school_id).order_by('-created_at')
            for cot in cots:
                if cot.quarter not in data["quarter"]:
                    data["quarter"].append(cot.quarter)
                if cot.school_year not in data["p_school_year"] and cot.is_for_teacher_proficient:
                    data["p_school_year"].append(cot.school_year)
                if cot.school_year not in data["hp_school_year"] and not cot.is_for_teacher_proficient:
                    data["hp_school_year"].append(cot.school_year)
                
                cot_taker = {
                    "school_year" : cot.school_year,
                    "quarter" : cot.quarter,
                    "cot_evaluator" : None,
                    "cot_taker" : None,
                    "cot" : cot.get_information(),
                }
                
                evaluator = models.People.objects.filter(employee_id=cot.employee_id).first()
                if evaluator:
                    cot_taker["cot_evaluator"] = evaluator.get_information()
                
                teacher = models.People.objects.filter(is_deactivated = False, employee_id=cot.evaluated_id).first()
                if teacher:
                    cot_taker["cot_taker"] = teacher.get_information()
                
                data["cot_taker"].append(cot_taker)
            
            
            
            
            return JsonResponse(data, status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
    'message' : 'Invalid request',
    }, status=400)




@csrf_exempt
def school_get_records_rpms(request):
    try:
        if request.method == "POST":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message': 'User not found',
                }, status=400)

            data = {
                "hp_school_year" : [],
                "p_school_year" : [],
                "rpms_taker": [],
            }

            school_year = request.POST.get('school_year', None)
            if school_year:
                rpms = models.RPMSFolder.objects.filter(school_id=user.school_id , rpms_folder_school_year=school_year).order_by('-created_at')
            else:
                rpms = models.RPMSFolder.objects.filter(school_id=user.school_id).order_by('-created_at')
            for rpm in rpms:
                if rpm.rpms_folder_school_year not in data["p_school_year"] and rpm.is_for_teacher_proficient:
                    data["p_school_year"].append(rpm.rpms_folder_school_year)
                if rpm.rpms_folder_school_year not in data["hp_school_year"] and not rpm.is_for_teacher_proficient:
                    data["hp_school_year"].append(rpm.rpms_folder_school_year)

                classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpm.rpms_folder_id, school_id=user.school_id).order_by('-created_at')
                for classwork in classworks:
                    attachment = models.RPMSAttachment.objects.filter(class_work_id=classwork.class_work_id, school_id=user.school_id).order_by('-created_at').first()
                    if attachment:
                        rpms_record = {
                            "school_year": rpm.rpms_folder_school_year,
                            "rpms_taker": None,
                            "rpms_data": attachment.get_information(),
                            "rpms_rater": None
                        }

                        rpms_taker = models.People.objects.filter(is_deactivated = False, employee_id=attachment.employee_id, school_id=user.school_id).first()
                        if rpms_taker:
                            rpms_record["rpms_taker"] = rpms_taker.get_information()

                        rpms_rater = models.People.objects.filter(employee_id=attachment.evaluator_id, school_id=user.school_id).first()
                        if rpms_rater:
                            rpms_record["rpms_rater"] = rpms_rater.get_information()

                        data["rpms_taker"].append(rpms_record)

            return JsonResponse(data, status=200)

    except Exception as e:
        return JsonResponse({
            'message': f'Something went wrong: {e}',
        }, status=500)

    return JsonResponse({
        'message': 'Invalid request',
    }, status=400)





@csrf_exempt
def school_get_records_ipcrf(request):
    try:
        if request.method == "POST":
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message': 'User not found',
                }, status=400)

            data = {
                "hp_school_year": [],
                "p_school_year": [],
                "quarter": [],
                "ipcrf_taker": [],
            }

            
            school_year = request.POST.get('school_year', None)
            if school_year : 
                ipcrfs = models.IPCRFForm.objects.filter(school_id=user.school_id, form_type="PART 1" , school_year=school_year).order_by('-created_at')
            else :
                ipcrfs = models.IPCRFForm.objects.filter(school_id=user.school_id, form_type="PART 1").order_by('-created_at')
            for ipcrf in ipcrfs:
                if ipcrf.school_year not in data["p_school_year"] and ipcrf.is_for_teacher_proficient :
                    data["p_school_year"].append(ipcrf.school_year)
                if ipcrf.school_year not in data["hp_school_year"] and not ipcrf.is_for_teacher_proficient :
                    data["hp_school_year"].append(ipcrf.school_year)

                ipcrf_record = {
                    "school_year": ipcrf.school_year,
                    "ipcrf_taker": None,
                    "ipcrf_rater": None,
                    "ipcrf": ipcrf.get_information(),
                }

                ipcrf_taker = models.People.objects.filter(is_deactivated = False, employee_id=ipcrf.employee_id, school_id=user.school_id).first()
                if ipcrf_taker:
                    ipcrf_record["ipcrf_taker"] = ipcrf_taker.get_information()

                ipcrf_rater = models.People.objects.filter(employee_id=ipcrf.evaluator_id, school_id=user.school_id).first()
                if ipcrf_rater:
                    ipcrf_record["ipcrf_rater"] = ipcrf_rater.get_information()

                data["ipcrf_taker"].append(ipcrf_record)

            return JsonResponse(data, status=200)

    except Exception as e:
        return JsonResponse({
            'message': f'Something went wrong: {e}',
        }, status=500)

    return JsonResponse({
        'message': 'Invalid request',
    }, status=400)





@csrf_exempt
def get_rating_sheet_by_school(request):
    try:
        if request.method == 'POST':
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message': 'User not found',
                }, status=400)

            teacher_id = request.POST.get('teacher_id')
            quarter = request.POST.get('quarter')
            # cot_id = request.POST.get('cot_id')
            
            # if not cot_id:
            #     return JsonResponse({
            #         'message' : 'cot_id is required',
            #         }, status=400) 
            
            if not teacher_id:
                return JsonResponse({
                    'message' : 'Teacher ID is required',
                    }, status=400)
            
            if not quarter:
                return JsonResponse({
                    'message' : 'Quarter is required',
                    }, status=400)
            
            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            cots = models.COTForm.objects.filter(school_id=user.school_id, quarter=quarter , evaluated_id=teacher_id).order_by('-created_at').first()
            
            return JsonResponse({
                'cot' : cots.get_information() if cots else {},
                'teacher' : teacher.get_information(),
            },status=200)
            
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
        }, status=400)






@csrf_exempt
def school_get_ipcrf(request):
    try:
        if request.method == 'POST':
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message': 'User not found',
                }, status=400)

            teacher_id = request.POST.get('teacher_id')
            ipcrf_id = request.POST.get('ipcrf_id')
            
            if not teacher_id:
                return JsonResponse({
                    'message' : 'Teacher ID is required',
                    }, status=400)
            
            if not ipcrf_id:
                return JsonResponse({
                    'message' : 'IPCRF ID is required',
                    }, status=400)
            
            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            ipcrf = models.IPCRFForm.objects.filter(school_id=user.school_id, form_type='PART 1' , connection_to_other=ipcrf_id).first()
            ipcrf_3 = models.IPCRFForm.objects.filter(school_id=user.school_id, form_type='PART 3' , connection_to_other=ipcrf_id).first()
            
            rater = models.People.objects.filter(employee_id=ipcrf.evaluator_id, school_id=user.school_id).first()
            
            return JsonResponse({
                'ipcrf' : ipcrf.get_information() if ipcrf else None,
                'ipcrf_3' : ipcrf_3.get_information() if ipcrf_3 else None,
                'teacher' : teacher.get_information(),
                'rater' : rater.get_information() if rater else None,
                'school' : user.get_school_information()
            },status=200)
    
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
        }, status=400)



@csrf_exempt
def deactivate_faculty(request):
    try:
        if request.method == 'POST':
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message': 'User not found',
                }, status=400)

            teacher_id = request.POST.get('teacher_id')
            
            if not teacher_id:
                return JsonResponse({
                    'message' : 'Teacher ID is required',
                    }, status=400)
            
            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, employee_id=teacher_id ).first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            teacher.is_deactivated = True
            teacher.save()
            
            return JsonResponse({
                'teacher' : teacher.get_information(),
            },status=200)
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
        }, status=400)




@csrf_exempt
def get_cot_from_school(request):
    try:
        if request.method == 'POST':
            user = models.School.objects.filter(email_address=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message': 'User not found',
                }, status=400)
            
            teacher_id = request.POST.get('teacher_id')
            quarter = request.POST.get('quarter')
            cot_id = request.POST.get('cot_id')
            
            if not teacher_id:
                return JsonResponse({
                    'message' : 'Teacher ID is required',
                    }, status=400)

            if not quarter:
                return JsonResponse({
                    'message' : 'Quarter is required',
                    }, status=400)
            
            if not cot_id:
                return JsonResponse({
                    'message' : 'COT ID is required',
                    }, status=400)

            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            cots = models.COTForm.objects.filter(school_id=user.school_id, quarter=quarter , evaluated_id=teacher_id , cot_form_id=cot_id).order_by('-created_at').first()
            rater = None
            if cots :
                rater = models.People.objects.filter(is_deactivated = False, is_accepted = True, school_id=user.school_id, employee_id=cots.employee_id , role='Evaluator').first()
                if rater:
                    rater = rater.get_information()
            return JsonResponse({
                'cot' : cots.get_information() if cots else None,
                'teacher' : teacher.get_information(),
                'rater' : rater
            },status=200)
            
                
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
        }, status=400)