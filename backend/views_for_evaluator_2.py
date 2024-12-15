
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import People
from django.contrib.auth import authenticate, login, logout 
from datetime import datetime, timedelta
from django.utils import timezone 

from . import models, my_utils


import secrets
import string
from itertools import groupby
from uuid import uuid4
from threading import Thread
import json









@csrf_exempt
def check_teacher_ipcrf_form_part_1_by_evaluator(request):
    try:
        
        if request.method == 'POST':
            
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            # TODO : WAIT FOR UPDATE IN IDENTIFICATION ID OF OBSERVER AND Teacher
            """
                {
                    'ipcrf_id' : 'ipcrf_id',
                    'content' : {...} !Content/Checked of IPCRF form from teacher
                    'total_score' : 0.328,
                    'plus_factor' : numbers,
                    'average_score' numbers,
                }
            """
            
            connection_to_other = request.POST.get('ipcrf_id')
            content : dict[str , dict] = json.loads(request.POST.get('content', None))
            rating = request.POST.get('total_score', None)
            plus_factor = request.POST.get('plus_factor', None)
            average_score = request.POST.get('average_score', None)
            
            kra1 = request.POST.get('kra1', None)
            kra2 = request.POST.get('kra2', None)
            kra3 = request.POST.get('kra3', None)
            kra4 = request.POST.get('kra4', None)
            plus_factor = request.POST.get('plus_factor', None)
            
            if not kra1:
                return JsonResponse({
                    'message' : 'KRA 1 not found',
                }, status=400)
            if not kra2:
                return JsonResponse({
                    'message' : 'KRA 2 not found',
                }, status=400)
            if not kra3:
                return JsonResponse({
                    'message' : 'KRA 3 not found',
                }, status=400)
            if not kra4:
                return JsonResponse({
                    'message' : 'KRA 4 not found',
                }, status=400)
            if not plus_factor:
                return JsonResponse({
                    'message' : 'Plus Factor not found',
                }, status=400)
            
            
            if not rating:
                return JsonResponse({
                    'message' : 'Rating not found',
                }, status=400)
            if not connection_to_other:
                return JsonResponse({
                    'message' : 'Connection to other not found',
                }, status=400)
            if not plus_factor:
                return JsonResponse({
                    'message' : 'Plus Factor score not found',
                }, status=400)
            if not average_score:
                return JsonResponse({
                    'message' : 'Average score not found',
                }, status=400)
            if not content:
                return JsonResponse({
                    'message' : 'Content not found',
                }, status=400)
             
            
            part_1 = models.IPCRFForm.objects.filter(connection_to_other=connection_to_other, form_type="PART 1").order_by('-created_at').first()
            
            if not part_1:
                return JsonResponse({
                    'message' : 'Invalid IPCRF ID',
                    }, status=400)
            
            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=part_1.employee_id, role='Teacher').first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                    }, status=400)
            
            school = models.School.objects.filter(school_id=teacher.school_id).first()
            if not school:
                return JsonResponse({
                    'message' : 'School not found',
                    }, status=400)
            
            part_1.kra1_evaluator = kra1
            part_1.kra2_evaluator = kra2
            part_1.kra3_evaluator = kra3
            part_1.kra4_evaluator = kra4
            part_1.plus_factor_evaluator = plus_factor
            part_1.check_date = timezone.now()
            part_1.evaluator_id = user.employee_id
            part_1.evaluator_rating = rating
            part_1.evaluator_plus_factor = plus_factor
            part_1.evaluator_average_score = average_score
            my_utils.update_ipcrf_form_part_1_by_evaluator(
                 ipcrf_form=part_1, content=content    
            )
             
            evaluation = ""
            if not teacher.is_evaluated:
                evaluation = teacher.update_is_evaluted()
            
            
            return JsonResponse({
                'message' : 'Form updated successfully',
                'evaluation' : evaluation
            },status=200)
            
            
            
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def get_all_teacher_in_school(request):
    try:
        if request.method == 'GET':
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username).first() 
            
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
  
            teachers = models.People.objects.filter(is_deactivated = False,is_accepted = True, school_id=user.school_id, role='Teacher').order_by('-created_at')
            
            teachers_data = []
            for teacher in teachers:
                data = teacher.get_information() 
                
                one_year_ago = timezone.now() - timedelta(days=365)
                ipcrf_forms_last_year = models.IPCRFForm.objects.filter(created_at__gte=one_year_ago , employee_id=teacher.employee_id).order_by('-created_at')
                data['ipcrf_quarter'] = [  ]
                if ipcrf_forms_last_year: 
                    school_year = ""
                    quarter = 1
                    for form in ipcrf_forms_last_year:
                        if len(school_year) == 0:
                            school_year = form.school_year
                            
                        if school_year == form.school_year:
                            data['ipcrf_quarter'].append({f"Quarter {quarter}" : form.get_information() })
                            quarter += 1 
                
                cot = models.COTForm.objects.filter(created_at__gte=one_year_ago , evaluated_id=teacher.employee_id).order_by('-created_at').first()
                data['cot_quarter'] = []
                if cot:
                    data['cot_quarter'].append({
                        "Quarter 1" : cot.get_information()
                    })
                
                rpms = models.RPMSAttachment.objects.filter(created_at__gte=one_year_ago , employee_id=teacher.employee_id).order_by('-created_at')
                data['rpms_quarter'] = []
                if rpms:
                    data['rpms_quarter'].append({
                        "Quarter 1" : [ rpm.get_information() for rpm in rpms]
                    })
                teachers_data.append(data)
                
            return JsonResponse({
                'teachers' : teachers_data ,
            }, status=200)
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400) 
    
    
    
@csrf_exempt
def get_rating_sheet_for_all_teacher(request):
    try:
        if request.method == 'GET':
            
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username, role='Evaluator').first()
            if not user:
                return JsonResponse({
                   'message' : 'User not found',
                    }, status=400)
            
            quarters = {
                "Quarter 1" : [],
                "Quarter 2" : [],
                "Quarter 3" : [],
                "Quarter 4" : [],
            }
            
            for quarter in quarters:
                cots = models.COTForm.objects.filter( is_for_teacher_proficient=my_utils.is_proficient_faculty(user, is_faculty=True ) , quarter=quarter , school_id=user.school_id).order_by('-created_at')
                for cot in cots:
                    if user.department == "N/A":
                        teacher = models.People.objects.filter(is_deactivated = False, school_id=user.school_id, employee_id=cot.evaluated_id).first()
                    else:
                        teacher = models.People.objects.filter(is_deactivated = False, school_id=user.school_id, employee_id=cot.evaluated_id , department=user.department).first()
                    
                    if teacher:
                        quarters[quarter].append({
                            'teacher' : teacher.get_information(),
                            'cot' : cot.get_information()
                        })

            return JsonResponse(quarters, status=200)
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)

    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    


@csrf_exempt
def evaluator_check_rpms_attachment(request):
    try:
        
        if request.method == 'POST':
            
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            # TODO : Update the content
            """
            evaluator/school/check/rpms/attachment/
                {
                    'rpms_id' : 'rpms_id',
                    'content' : {...} !Content/Checked of RPMS form from teacher
                    'index' : string,
                }
            """
            
            rpms_id = request.POST.get('rpms_id')
            content : dict[str , dict] = json.loads(request.POST.get('content', None))
            comment = request.POST.get('comment', '')
            index = request.POST.get('index', None)
            
            if not rpms_id:
                return JsonResponse({
                   'message' : 'Please provide rpms_id',
                    }, status=400)
                
            if not rpms_id:
                return JsonResponse({
                   'message' : 'Please provide rpms_id',
                    }, status=400)
            
            if not content:
                return JsonResponse({
                    'message' : 'content is required',
                    }, status=400)
             
            
            rpms = models.RPMSAttachment.objects.filter(attachment_id=rpms_id).order_by('-created_at').first()
            if not rpms:
                return JsonResponse({
                    'message' : 'Invalid RPMS ID',
                    }, status=400)
            
            if index == '1':
                rpms.file_is_checked = True
                rpms.comment_1 = comment 
            elif index == '2':
                rpms.file2_is_checked = True
                rpms.comment_2 = comment 
            elif index == '3':
                rpms.file3_is_checked = True
                rpms.comment_3 = comment 
            if index == '4':
                rpms.file4_is_checked = True 
                rpms.comment_4 = comment 
                
            if rpms.title == "KRA 1: Content Knowledge and Pedagogy" or rpms.title == "KRA 2: Learning Environment and Diversity of Learners":
                if ( rpms.file_is_checked and rpms.file2_is_checked and 
                    rpms.file3_is_checked and rpms.file4_is_checked):
                    rpms.is_submitted = True
                    rpms.is_checked = True
                
            if rpms.title == "KRA 3: Curriculum and Planning" or rpms.title == "KRA 4:  Curriculum and Planning & Assessment and Reporting":
                if ( rpms.file_is_checked and rpms.file2_is_checked and 
                    rpms.file3_is_checked):
                    rpms.is_submitted = True
                    rpms.is_checked = True

            if rpms.title == "PLUS FACTOR":
                if ( rpms.file_is_checked ):
                    rpms.is_submitted = True
                    rpms.is_checked = True
                
            
            rpms.evaluator_id = user.employee_id
            my_utils.update_rpms_attachment(rpms_attachment=rpms, content=content)
            
            teacher = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=rpms.employee_id, role='Teacher').first()
            evaluation = ""
            if not teacher.is_evaluated:
                evaluation = teacher.update_is_evaluted()
            
            return JsonResponse({
                'message' : 'Form updated successfully',
                'evaluation' : evaluation
            },status=200)
            
        
        
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)


@csrf_exempt
def evaluator_get_list_of_rpms_takers(request):
    try:
        
        if request.method == 'GET':
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
                

            teachers = models.People.objects.filter(is_deactivated = False, school_id=user.school_id, role='Teacher', department=user.department).order_by('-created_at')
            
            
            teachers_rpms = []
            """
            [
                {
                    'teacher' : {...},
                    'rater' : '',
                    'status' : 'Pending'
                }
            ]
            
            STATUS: 
            Pending - kapag naipasa na ni teacher lahat ng attachment pero hindi pa nagsisimulang mag-evaluate si Evaluator

            In progress - kapag nagsimula nang mag-score ng isa attachment si evaluator

            Completed - kapag tapos na lahat mascoran ni evaluator yung limang attachments
            """
            
            for teacher in teachers:
                teacher_data = {
                    'teacher' : teacher.get_information(),
                    'rater' : None,
                    'status' : 'Pending',
                    'number_of_submitted' : 0,
                    'number_of_checked' : 0,
                    'number_of_classwork' : 0,
                    'rpms' : []
                }
                # TODO : FIX IT SOON
                
                first_attachment = models.RPMSAttachment.objects.filter(employee_id=teacher.employee_id).order_by('-created_at').first()
                if first_attachment :
                    first_classwork = models.RPMSClassWork.objects.filter(class_work_id=first_attachment.class_work_id).order_by('-created_at').first()
                    
                    folder = models.RPMSFolder.objects.filter(rpms_folder_id=first_classwork.rpms_folder_id).first()
                    classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=folder.rpms_folder_id).order_by('-created_at')
                    for classwork in classworks:
                        rpms_attachments = models.RPMSAttachment.objects.filter(
                            class_work_id=classwork.class_work_id, 
                            employee_id=teacher.employee_id).order_by('-created_at')
                        teacher_data['number_of_classwork'] += 1
                        if rpms_attachments:
                            teacher_data['number_of_submitted'] += 1
                            for rpms_attachment in rpms_attachments:
                                teacher_data['rpms'].append(rpms_attachment.get_information())
                                if rpms_attachment.is_checked:
                                    teacher_data['number_of_checked'] += 1
                                    teacher_data['status'] = 'In Progress'
                                    teacher_data['rater'] = models.People.objects.filter(employee_id=rpms_attachment.evaluator_id).first().get_information()
                                break
                if teacher_data['number_of_checked'] >= 5:
                    teacher_data['status'] = 'Completed'
                teachers_rpms.append(teacher_data)
            
            return JsonResponse({ 'teachers' : teachers_rpms}, status=200)
                
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
        
    return JsonResponse({
        'message' : 'Invalid request',
        }, status=400)
    




@csrf_exempt
def evaluator_get_rpms_work(request):
    try:
        
        if request.method == 'POST':
            
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()

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
def evaluator_get_rpms_folders(request):
    # Used to view all the folder
    try:
        
        if request.method == 'POST':
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first() 
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            folder_type = request.POST.get('folder_type')
            
            if folder_type not in ['proficient', 'highly_proficient']:
                return JsonResponse({
                    'message' : 'Invalid folder_type must contain proficient or highly_proficient',
                }, status=400)
            
            
            
            rpms_folders = models.RPMSFolder.objects.filter(
                school_id=user.school_id,
                is_for_teacher_proficient= True if folder_type == 'proficient' else False
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
def evaluator_get_rpms_folder(request):
    try:
        if request.method == 'POST':
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()

            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)

            rpms_folder_id = request.POST.get('rpms_folder_id')
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'rpms_folder_id not found',
                }, status=400)
             
            # formData.append('teacher_id', teacher_id ); 
            # formData.append('school_year', school_year);
        
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id not found',
                }, status=400)
        
            school_year = request.POST.get('school_year')
            if not school_year:
                return JsonResponse({
                    'message' : 'school_year not found',
                }, status=400)
                
            rpms_folder = models.RPMSFolder.objects.filter(rpms_folder_school_year=school_year, rpms_folder_id=rpms_folder_id).order_by('-created_at').first()
            if not rpms_folder:
                return JsonResponse({
                    'message' : 'RPMS Folder not found',
                }, status=400)
        
            classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpms_folder_id).order_by('-created_at')
            rpms_classworks = []
            for classwork in classworks:
                attachement = models.RPMSAttachment.objects.filter(employee_id=teacher_id, class_work_id=classwork.class_work_id).order_by('-created_at').first()
                if attachement:
                    rpms_classworks.append(classwork.get_rpms_classwork_information( attachement ))
            
            return JsonResponse({
                'rpms_folder' : rpms_folder.get_rpms_folder_information(),
                'rpms_classworks' : rpms_classworks
            },status=200)
            
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}',
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request',
    },status=400)

 

@csrf_exempt
def evaluator_get_rpms_work_attachments(request):
    try:
        
        if request.method == 'POST':
            user = models.People.objects.filter(is_deactivated = False, employee_id=request.user.username).first()
             
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            class_work_id = request.POST.get('class_work_id')
            teacher_id = request.POST.get('teacher_id')
            
            if not class_work_id:
                return JsonResponse({
                    'message' : 'class_work_id not found',
                },status=400)
            
            
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id not found',
                },status=400)
            
            teacher = models.People.objects.filter(is_deactivated = False, employee_id=teacher_id).first()
            if not teacher:
                return JsonResponse({
                    'message' : 'Teacher not found',
                },status=400)
            submitted_attachments = models.RPMSAttachment.objects.filter( is_submitted=True, class_work_id=class_work_id, employee_id=teacher_id).order_by('-created_at')
            unsubmitted_attachments = models.RPMSAttachment.objects.filter( is_submitted=False, class_work_id=class_work_id, employee_id=teacher_id).order_by('-created_at')
            
            return JsonResponse({
                    'teacher' : teacher.get_information(),
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
def evaluator_get_rpms_attachment_result(request):
    try:
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            rpms_folder_id = request.POST.get('rpms_folder_id')
            teacher_id = request.POST.get('teacher_id')
            
            if not rpms_folder_id:
                return JsonResponse({
                    'message' : 'rpms_folder_id not found',
                },status=400) 
            
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id not found',
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
                
            rpms_attachments = models.RPMSAttachment.objects.filter(class_work_id__in=[classwork.class_work_id for classwork in classworks], employee_id=teacher_id).order_by('-created_at')
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
def evaluator_summary_recommendations(request):
    try:
        
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
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
def evaluator_summary_performance(request):
    try:
        
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id is required',
                    }, status=400)

            teacher = models.People.objects.filter(is_deactivated = False,is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
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
def evaluator_summary_rpms(request):
    try:
        
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
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
def evaluator_summary_swot(request):
    try:
        if request.method == "POST":
            user = models.People.objects.filter(employee_id=request.user.username).first()
             
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                }, status=400)
                
            
            teacher_id = request.POST.get('teacher_id')
            if not teacher_id:
                return JsonResponse({
                    'message' : 'teacher_id is required',
                    }, status=400)

            teacher = models.People.objects.filter(is_deactivated = False,is_accepted = True, school_id=user.school_id, employee_id=teacher_id , role='Teacher').first()
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
def evaluator_get_records_cot(request):
    try:
        if request.method == "POST":
            
            user = models.People.objects.filter(is_deactivated = False,is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
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
                
                teacher = models.People.objects.filter(is_deactivated = False, employee_id=cot.evaluated_id).first()
                if teacher:
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
def evaluator_get_records_rpms(request):
    try:
        if request.method == "POST":
            
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
                    }, status=400)
            
            data = {
                "hp_school_year" : [],
                "p_school_year" : [],
                "rpms_taker": [],
            }
            
            school_year = request.POST.get('school_year', None)
            if school_year:
                rpms = models.RPMSFolder.objects.filter(is_for_teacher_proficient=my_utils.is_proficient_faculty(user , is_faculty=True) , school_id=user.school_id , rpms_folder_school_year=school_year).order_by('-created_at')
            else:
                rpms = models.RPMSFolder.objects.filter(is_for_teacher_proficient=my_utils.is_proficient_faculty(user, is_faculty=True) , school_id=user.school_id).order_by('-created_at')
            for rpm in rpms:
                if rpm.rpms_folder_school_year not in data["p_school_year"] and rpm.is_for_teacher_proficient:
                    data["p_school_year"].append(rpm.rpms_folder_school_year)
                if rpm.rpms_folder_school_year not in data["hp_school_year"] and not rpm.is_for_teacher_proficient:
                    data["hp_school_year"].append(rpm.rpms_folder_school_year)

                classworks = models.RPMSClassWork.objects.filter(rpms_folder_id=rpm.rpms_folder_id, school_id=user.school_id).order_by('-created_at')
                for classwork in classworks:
                    attachments = models.RPMSAttachment.objects.filter(class_work_id=classwork.class_work_id, school_id=user.school_id).order_by('-created_at')
                    for attachment in attachments:
                        if attachment:
                            rpms_taker = models.People.objects.filter(is_deactivated = False, employee_id=attachment.employee_id, school_id=user.school_id).first()
                            if rpms_taker:
                                rpms_record = {
                                    "school_year": rpm.rpms_folder_school_year,
                                    "rpms_taker": None,
                                    "rpms_data": attachment.get_information(),
                                    "rpms_rater": None
                                }

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
def evaluator_get_records_ipcrf(request):
    try:
        if request.method == "POST":
            
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
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

                ipcrf_taker = models.People.objects.filter(is_deactivated = False, employee_id=ipcrf.employee_id, school_id=user.school_id).first()
                if ipcrf_taker:
                    ipcrf_record = {
                        "school_year": ipcrf.school_year,
                        "ipcrf_taker": None,
                        "ipcrf_rater": None,
                        "ipcrf": ipcrf.get_information(),
                    }

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
def evaluator_get_ipcrf(request):
    try:
        if request.method == 'POST':
            user = models.People.objects.filter(is_deactivated = False, is_accepted = True, employee_id=request.user.username , role='Evaluator').first()
            if not user:
                return JsonResponse({
                    'message' : 'User not found',
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

            school = models.School.objects.filter(school_id=user.school_id).first()
            ipcrf = models.IPCRFForm.objects.filter(school_id=user.school_id, form_type='PART 1' , connection_to_other=ipcrf_id).first()
            ipcrf_3 = models.IPCRFForm.objects.filter(school_id=user.school_id, form_type='PART 3' , connection_to_other=ipcrf_id).first()
            rater = None
            if ipcrf:
                rater = models.People.objects.filter(employee_id=ipcrf.evaluator_id, school_id=user.school_id).first()
            
            return JsonResponse({
                'ipcrf' : ipcrf.get_information() if ipcrf else None,
                'ipcrf_3' : ipcrf_3.get_information() if ipcrf_3 else None,
                'teacher' : teacher.get_information(),
                'rater' : rater.get_information() if rater else None,
                'school' : school.get_school_information() if school else None
            },status=200)
    
    
    except Exception as e:
        return JsonResponse({
            'message' : f'Something went wrong : {e}'
            }, status=500)
    
    return JsonResponse({
        'message' : 'Invalid request method',
        }, status=400)
