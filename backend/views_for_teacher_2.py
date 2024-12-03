
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
from django.utils import timezone 

from . import models, my_utils


import secrets
import string
from itertools import groupby
from uuid import uuid4
from threading import Thread
import json




# ================================= Teacher Views =============================== #

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
            
            if not content:
                return JsonResponse({
                    'message' : 'Content not found',
                }, status=400)
                
            ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type='PART 3').order_by('-created_at').first()
            if not ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form not found',
                }, status=400)
            
            if ipcrf.is_checked:
                return JsonResponse({
                    'message' : 'IPCRF Form is already checked',
                }, status=400)
            
            part_1_ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type="PART 1").first()
            if not part_1_ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form PART 1 not found',
                }, status=400)
            
            if not part_1_ipcrf.is_checked:
                return JsonResponse({
                    'message' : 'IPCRF Form PART 1 is not checked',
                }, status=400)
            
            part_2_ipcrf = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type="PART 2").first()
            if not part_2_ipcrf:
                return JsonResponse({
                    'message' : 'IPCRF Form PART 2 not found',
                }, status=400)
            
            if not part_2_ipcrf.is_checked:
                return JsonResponse({
                    'message' : 'IPCRF Form PART 2 is not checked',
                }, status=400)
            
            ipcrf.submit_date = timezone.now()
            my_utils.update_ipcrf_form_part_3_by_teacher(ipcrf, content)
            evaluation = ""
            if not user.is_evaluated:
                evaluation = user.update_is_evaluted()
            return JsonResponse({
                'message' : 'IPCRF Form updated successfully',
                'connection_to_other' : ipcrf.connection_to_other,
                'evaluation' : evaluation,
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
                school_id=user.school_id,
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
                'rpms_folder' : rpms_folder.get_rpms_folder_information(),
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
            
            files = []
            class_work_id = request.POST.get('class_work_id')
            # file = request.FILES.get('file')
            index = request.POST.get('index') # 1,2,3,4 represent the objectives
            for i in range(4):
                file = request.FILES.get(f'file{i+1}') # file1, file2, file3 , file4
                if file:
                    files.append(file) 
            
            if not index: 
                return JsonResponse({
                    'message' : 'index not found',
                },status=400)
             
            if not class_work_id:
                return JsonResponse({
                    'message' : 'class_work_id not found',
                },status=400)
            
            if not files or len(files) == 0:
                return JsonResponse({
                    'message' : 'files not found or empty files used name convention "file1", ... ',
                },status=400)
            
            classwork = models.RPMSClassWork.objects.filter(class_work_id=class_work_id).order_by('-created_at').first()
            if not classwork:
                return JsonResponse({
                    'message' : 'Class Work not found',
                },status=400)
                
            folder = models.RPMSFolder.objects.filter(rpms_folder_id=classwork.rpms_folder_id).order_by('-created_at').first()
            if not folder:
                return JsonResponse({
                    'message' : 'Folder not found',
                },status=400)
            
            past_attachments = models.RPMSAttachment.objects.filter( is_submitted=True, employee_id=user.employee_id, class_work_id=class_work_id).order_by('-created_at')
            
            if past_attachments:
                return JsonResponse({
                    'message' : 'Unsubmit before adding new ',
                },status=400)
            
            past_attachments = models.RPMSAttachment.objects.filter( is_submitted=False, employee_id=user.employee_id, class_work_id=class_work_id).order_by('-created_at').first()
            
            
            
            # attachment_id = past_attachments.attachment_id if past_attachments else str(uuid4())
            # post_id = past_attachments.post_id if past_attachments else str(uuid4())
            
            # for file in files:
            #     attachment = models.RPMSAttachment.objects.create(
            #         school_id=user.school_id,
            #         employee_id=user.employee_id,
            #         class_work_id=class_work_id, # IDENTIFIER FOR WHAT TYPE OF CLASSWORK
            #         file=file,
            #         is_submitted = True
            #     )
                
            #     attachment.submit_date = timezone.now()
            #     attachment.is_for_teacher_proficient = my_utils.is_proficient_faculty(user)
            #     attachment.title = classwork.title
            #     attachment.grade = classwork.get_grade()
            #     attachment.attachment_id = attachment_id
            #     attachment.post_id = post_id
            #     attachment.save()
            
            
            
            return JsonResponse({
                'message' : 'Files uploaded successfully',
            },status=200)
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_get_rpms_work_attachments(request):
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
            
            submitted_attachments = models.RPMSAttachment.objects.filter( is_submitted=True, class_work_id=class_work_id, employee_id=user.employee_id).order_by('-created_at')
            unsubmitted_attachments = models.RPMSAttachment.objects.filter( is_submitted=False, class_work_id=class_work_id, employee_id=user.employee_id).order_by('-created_at')
            
            return JsonResponse({
                    'submitted' : [attachment.get_information() for attachment in submitted_attachments],
                    'unsumitted' : [ attachment.get_information() for attachment in unsubmitted_attachments]
                },status=200)
            
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_get_rpms_attachment_result(request):
    try:
        if request.method == "POST":
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
                },status=400) 

            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_id=rpms_folder_id , school_id=user.school_id  ).order_by('-created_at').first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS Folder not found',
                },status=400)

            classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at')
            if not classworks:
                return JsonResponse({
                    'message' : 'Classworks not found',
                },status=400)
                
            rpms_attachments = models.RPMSAttachment.objects.filter(class_work_id__in=[classwork.class_work_id for classwork in classworks], employee_id=user.employee_id).order_by('-created_at')
            titles = []
            each_attachment_in_rpms = []
            for rpms_attachment in rpms_attachments:
                title = rpms_attachment.title
                if title not in titles:
                    titles.append(title)
                    each_attachment_in_rpms.append(
                        {
                            "title" : title,
                            "grade" : rpms_attachment.getGradeSummary()
                        }
                    )
            
            return JsonResponse({
                'rpms_folder_id' : rpms_folder_id,
                'scores' : each_attachment_in_rpms
            }, status=200)
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def teacher_unsubmit_class_work(request):
    try:
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            class_work_id = request.POST.get('class_work_id')

            if not class_work_id:
                return JsonResponse({
                    'message' : 'class_work_id not found',
                },status=400)
            
            
            attachments = models.RPMSAttachment.objects.filter(class_work_id=class_work_id, is_submitted=True, employee_id=user.employee_id).order_by('-created_at')
            for attachment in attachments:
                attachment.is_submitted = False
                attachment.save()
            
            return JsonResponse({
                'message' : 'Files unsubmitted successfully',
            },status=200)
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)






@csrf_exempt
def teacher_generate_report(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            data = {
                
            }
            
            data['job'] = user.get_job_years()
            data['recommendation'] = my_utils.get_recommendation_result_with_percentage(employee_id=user.employee_id)
            
            ipcrf = models.IPCRFForm.objects.filter(employee_id=user.employee_id, form_type='PART 1').order_by('-created_at').first()
            data['rating'] = ipcrf.get_information() if ipcrf else None
            data['performance_rating'] = my_utils.classify_ipcrf_score(ipcrf.evaluator_rating if ipcrf else 0.0)
            data['ranking'] = my_utils.recommend_rank(user)
            data['teacher'] = user.get_information()
            data['rater'] = None
            if ipcrf:
                rater = models.People.objects.filter(employee_id=ipcrf.evaluator_id).first()
                if rater:
                    data['rater'] = rater.get_information()
            
            return JsonResponse(data,status=200)
            
    
    except Exception as e: 
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400 )






@csrf_exempt
def teacher_get_records_cot(request):
    try:
        if request.method == "GET":
            
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            
            data = {
                "school_year" : [],
                "quarter" : [],
                "cot_taker" : [],
            }
            
            cots = models.COTForm.objects.filter(school_id=user.school_id).order_by('-created_at')
            for cot in cots:
                if cot.quarter not in data["quarter"]:
                    data["quarter"].append(cot.quarter)
                if cot.school_year not in data["school_year"]:
                    data["school_year"].append(cot.school_year)
                
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
                
                teacher = models.People.objects.filter(employee_id=cot.evaluated_id).first()
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
def teacher_get_records_rpms(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            data = {
                "school_year": [],
                "rpms_taker": [],
            }

            rpms = models.RPMSFolder.objects.filter(school_id=user.school_id).order_by('-created_at')
            for rpm in rpms:
                if rpm.rpms_folder_school_year not in data["school_year"]:
                    data["school_year"].append(rpm.rpms_folder_school_year)

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

                        rpms_taker = models.People.objects.filter(employee_id=attachment.employee_id, school_id=user.school_id).first()
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
def teacher_get_records_ipcrf(request):
    try:
        if request.method == "GET":
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            data = {
                "school_year": [],
                "quarter": [],
                "ipcrf_taker": [],
            }

            ipcrfs = models.IPCRFForm.objects.filter(school_id=user.school_id, form_type="PART 1").order_by('-created_at')
            for ipcrf in ipcrfs:
                if ipcrf.school_year not in data["school_year"]:
                    data["school_year"].append(ipcrf.school_year)

                ipcrf_record = {
                    "school_year": ipcrf.school_year,
                    "ipcrf_taker": None,
                    "ipcrf_rater": None,
                    "ipcrf": ipcrf.get_information(),
                }

                ipcrf_taker = models.People.objects.filter(employee_id=ipcrf.employee_id, school_id=user.school_id).first()
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
def teacher_get_ipcrf(request):
    try:
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
 
            ipcrf_id = request.POST.get('ipcrf_id')
             
            
            if not ipcrf_id:
                return JsonResponse({
                    'message' : 'IPCRF ID is required',
                    }, status=400)
            
            school = models.School.objects.filter(school_id=user.school_id).first()

            ipcrf = models.IPCRFForm.objects.filter(school_id=user.school_id, form_type='PART 1' , connection_to_other=ipcrf_id).first()
            ipcrf_3 = models.IPCRFForm.objects.filter(school_id=user.school_id, form_type='PART 3' , connection_to_other=ipcrf_id).first()
            
            rater = models.People.objects.filter(employee_id=ipcrf.evaluator_id, school_id=user.school_id).first()
            
            return JsonResponse({
                'ipcrf' : ipcrf.get_information() if ipcrf else None,
                'ipcrf_3' : ipcrf_3.get_information() if ipcrf_3 else None,
                'teacher' : user.get_information(),
                'rater' : rater.get_information() if rater else None,
                'school' : school.get_school_information()
            },status=200)
    
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
        }, status=400)





@csrf_exempt
def get_cot_from_by_teacher(request):
    try:
        if request.method == 'POST':
            user = models.People.objects.filter(employee_id=request.user.username).first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            teacher_id = user.employee_id
            quarter = request.POST.get('quarter')
            cot_id = request.POST.get('cot_id')
             
            if not quarter:
                return JsonResponse({
                    'message' : 'Quarter is required',
                    }, status=400)
            
            if not cot_id:
                return JsonResponse({
                    'message' : 'COT ID is required',
                    }, status=400)

            teacher = models.People.objects.filter(is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)

            cots = models.COTForm.objects.filter(school_id=user.school_id, quarter=quarter , evaluated_id=teacher_id , cot_form_id=cot_id).order_by('-created_at').first()
            rater = None
            if cots :
                rater = models.People.objects.filter(is_accepted = True, school_id=user.school_id, employee_id=cots.employee_id , role='Evaluator').first()
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




