from django.db import models 
from django.conf import settings
from django.utils import timezone
from .models_2 import *

from dateutil.relativedelta import relativedelta

import uuid, string ,random
# Create your models here.



position_in_model = {
    'Proficient' : ('Teacher I', 'Teacher II', 'Teacher III'  ),
    'Highly Proficient' : ('Master Teacher I', 'Master Teacher II', 'Master Teacher III', 'Master Teacher IV'),
}

evaluator_positions_in_model = {
    "Proficient": ["Head Teacher I", "Head Teacher II", "Head Teacher III", "Head Teacher IV", "Head Teacher V", "Head Teacher VI"],
    "Highly Proficient": ["School Principal I", "School Principal II", "School Principal III", "School Principal IV"]
}



def is_proficient_faculty_teacher_in_model(role : str):
    if role in position_in_model['Proficient']:
        return True
    return False

def is_highly_proficient_faculty_teacher_in_model(role : str):
    if role in position_in_model['Highly Proficient']:
        return True
    return False

def is_proficient_faculty_evaluator_in_model(role : str):
    if role in evaluator_positions_in_model['Proficient']:
        return True
    return False

def is_highly_proficient_faculty_evaluator_in_model(role : str):
    if role in evaluator_positions_in_model['Highly Proficient']:
        return True
    return False



class VerificationLink(models.Model):
    email = models.CharField(max_length=255, blank=True, default='')
    verification_link = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    data = models.JSONField(default=dict, blank=True)
    """
    {
        'password' : 'password',
        'confirm_password' : 'password'
    }
    """
    
    @classmethod
    def generate_link(cls, email):
        link_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
        cls.objects.create(email=email, verification_link=link_key) 
        return f"{settings.MY_HOST}register/school/verifications/{link_key}/"
    
    
    @classmethod
    def generate_change_key_link(cls, email, data : dict):
        link_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
        cls.objects.create(email=email, verification_link=link_key, data=data)
        return f"{settings.MY_HOST}/change-password-verifications/{link_key}/"
    
    def is_expired(self, expire_in_minutes=30):
        return self.created_at < (timezone.now() - timezone.timedelta(minutes=expire_in_minutes))


    def __str__(self) -> str:
        return f"{self.email} - {self.verification_link}"


def calculate_individual_averages_for_ipcrf(content):
    total_quality = 0
    total_efficiency = 0
    total_timelines = 0
    total_quality_count = 0
    total_efficiency_count = 0
    total_timelines_count = 0

    for key, value in content.items():
        if 'QUALITY' in value:
            total_quality += int(value['QUALITY']['Rate'])
            total_quality_count += 1
        if 'EFFICIENCY' in value:
            total_efficiency += int(value['EFFICIENCY']['Rate'])
            total_efficiency_count += 1
        if 'TIMELINES' in value:
            total_timelines += int(value['TIMELINES']['Rate'])
            total_timelines_count += 1

    average_quality = total_quality / total_quality_count if total_quality_count > 0 else 0
    average_efficiency = total_efficiency / total_efficiency_count if total_efficiency_count > 0 else 0
    average_timelines = total_timelines / total_timelines_count if total_timelines_count > 0 else 0

    return {
        "average_quality": average_quality,
        "average_efficiency": average_efficiency,
        "average_timelines": average_timelines
    }



 

class IPCRFForm(models.Model):
    """
        Form for the teacher to fill out
    """
    school_id = models.CharField(max_length=255, blank=True, default='')
    employee_id = models.CharField(max_length=255, blank=True, default='')
    evaluator_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    form_type = models.CharField(max_length=255, blank=True, default='',
            choices=(
              ('PART 1', 'PART 1'), # Teacher to Evaluator
              ('PART 2', 'PART 2'), # For Teacher
              ('PART 3', 'PART 3'), # For Teacher
            ))
    
    content_for_teacher = models.JSONField(default=dict, blank=True)
    """
    
    # PART 1 DATA
    {
        "Content Knowledge and Pedagogy": {
            "1": {
                "Question": "Applied knowledge of content within and across curriculum teaching areas (PPST 1.1.2)",
                "QUALITY": {
                    "1": "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                    "2": "Demonstrated Level 4 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms",
                    "3": "Demonstrated Level 5 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms",
                    "4": "Demonstrated Level 6 in Objective 1 as  shown in COT rating sheets / inter-observer agreement forms",
                    "5": "Demonstrated Level 7 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms",
                    "Rate": "0"
                },
                "EFFICIENCY": {
                    "1": "No acceptable evidence was shown",
                    "3": "Objective was met but instruction exceeded the allotted time",
                    "5": "Objective was met within the allotted time",
                    "Rate": "1"
                }
            },
            ....
        "Learning Environment & Diversity of Learners": {
            "5": {
                "Question": "Established safe and secure learning environments to enhance learning through the consistent implementation of policies",
                "QUALITY": {
                    "1": "Demonstrated Level 3 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                    "2": "Demonstrated Level 4 as shown in COT rating sheets / inter-observer agreement forms",
                    "3": "Demonstrated Level 5 as shown in COT rating sheets / inter-observer agreement forms",
                    "4": "Demonstrated Level 6 as shown in COT rating sheets / inter-observer agreement forms",
                    "5": "Demonstrated Level 7 as shown in COT rating sheets / inter-observer agreement forms",
                    "Rate": "0"
                },
                "EFFICIENCY": {
                    "1": "No acceptable evidence was shown",
                    "3": "Objective was met but instruction exceeded the allotted time",
                    "5": "Objective was met within the allotted time",
                    "Rate": "0"
                } 
            },
        },
    
    """
    
    """
    
        # PART 2
        {
            "1" : {
                "Title" : "SELF-MANAGEMENT",
                "1" : "Sets personal goals and direction, needs and development.",
                "2" : "Sets personal goals and direction, needs and development.",
                "3" : "Sets personal goals and direction, needs and development.",
                "4" : "Sets personal goals and direction, needs and development.",
                "5" : "Sets personal goals and direction, needs and development.",
                "Selected" : []
            },
            "2" : {
                "Title" : "Professionalism and Ethics",
                "1" : "Sets personal goals and direction, needs and development.",
                "2" : "Sets personal goals and direction, needs and development.",
                "3" : "Sets personal goals and direction, needs and development.",
                "4" : "Sets personal goals and direction, needs and development.",
                "5" : "Sets personal goals and direction, needs and development.",
                "Selected" : [
                    "1" , "2", "3"
                ]
            }
        }
        
    """
    
    """
    
        # PART 3
        {
            "A" : {
                "Strenghts" : [],
                "Development Needs" : [],
                "Learning Objectives": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
                "Intervention": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
                "Timeline": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
                "Resources Needs": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
                
            },
            
            "B" : { 
                "Strenghts" : [],
                "Development Needs" : [],
                "Learning Objectives": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
                "Intervention": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
                "Timeline": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
                "Resources Needs": {
                    "1" : "Learning Objectives Learning Objectives Learning Objectives.",
                    "2" : "Learning Objectives Learning Objectives Learning Objectives.",
                },
            }
            
        }
        
    
    """
    
    content_for_evaluator = models.JSONField(default=dict, blank=True)
    """
    
    # PART 1 DATA
    {
        
        "1" : {
            "Question" : "Applied knowledge of content within and across curriculum teaching areas (PPST 1.1.2)",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "Rate" : "0"
            },
            "TIMELINES" : {
                "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "Rate" : "0"
            }
        },
        "2" : {
            "Question" : "Applied knowledge of content within and across curriculum teaching areas (PPST 1.1.2)",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "Rate" : "0"
            },
            "EFFICIENCY" : {
                "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "Rate" : "0"
            },
            "TIMELINES" : {
                "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "Rate" : "0"
            }
        }
        
        
    }
    
    
    """


    status = models.CharField(max_length=255, blank=True, default='Pending',
        choices=(
         ('Pending', 'Pending'),
         ('Approved', 'Approved'),
         ('Rejected', 'Rejected'),
         ('Cancelled', 'Cancelled'),
         ('Completed', 'Completed'),
        ))
    
    
    is_checked_by_evaluator = models.BooleanField(default=False)
    is_checked = models.BooleanField(default=False) # Check if the teacher submit it
    connection_to_other = models.CharField(max_length=255, blank=True, default='') # Generate a random ID, used for identifying parts (1,2,3)
    is_for_teacher_proficient = models.BooleanField(default=False) # If True, the folder is for teacher proffecient
    is_expired = models.BooleanField(default=False) # Used to check if the form is expired
    school_year = models.CharField(max_length=255, blank=True, default='') # School year
    
    check_date = models.DateTimeField(blank=True, null=True, default=None)
    is_submitted = models.BooleanField(default=False) # Used to identify it already submmited
    submit_date = models.DateTimeField(blank=True, null=True, default=None)

    rating = models.FloatField( blank=True, default=0.0) # Rating
    average_score = models.FloatField( blank=True, default=0.0) # Average Score
    plus_factor = models.FloatField( blank=True, default=0.0) # Plus Factor Score
    
    evaluator_rating = models.FloatField( blank=True, default=0.0) # Rating
    evaluator_average_score = models.FloatField( blank=True, default=0.0) # Average Score
    evaluator_plus_factor = models.FloatField( blank=True, default=0.0) # Plus Factor Score
    
    kra1_teacher = models.FloatField( blank=True, default=0.0) 
    kra2_teacher = models.FloatField( blank=True, default=0.0)
    kra3_teacher = models.FloatField( blank=True, default=0.0)
    kra4_teacher = models.FloatField( blank=True, default=0.0)
    plus_factor_teacher = models.FloatField( blank=True, default=0.0)
    
    kra1_evaluator = models.FloatField( blank=True, default=0.0) 
    kra2_evaluator = models.FloatField( blank=True, default=0.0)
    kra3_evaluator = models.FloatField( blank=True, default=0.0)
    kra4_evaluator = models.FloatField( blank=True, default=0.0)
    plus_factor_evaluator = models.FloatField( blank=True, default=0.0)
    
    
    
    def __str__(self):
        return f"{self.school_id} - {self.employee_id} - {self.form_type} - {self.evaluator_id} - {self.connection_to_other}"
    
    def get_information(self):
        data =  {
            'form' : 'IPCRFForm',
            'school_id' : self.school_id,
            'employee_id' : self.employee_id,
            'created_at' : self.created_at,
            'form_type' : self.form_type,
            'evaluator_id' : self.evaluator_id,
            'content_for_teacher' : self.content_for_teacher,
            'content_for_evaluator' : self.content_for_evaluator,
            'is_checked' : self.is_checked,
            'connection_to_other' : self.connection_to_other,
            'is_for_teacher_proficient' : self.is_for_teacher_proficient,
            'status' : self.status,
            'is_checked_by_evaluator' : self.is_checked_by_evaluator,
            'is_expired' : self.is_expired,
            'school_year' : self.school_year,
            'rating' : self.rating,
            'average_score' : self.average_score,
            'plus_factor' : self.plus_factor,
            'evaluator_rating' : self.evaluator_rating,
            'evaluator_average_score' : self.evaluator_average_score,
            'evaluator_plus_factor' : self.evaluator_plus_factor,
            'is_submitted' : self.is_submitted,
            'rater' : None,
            'submit_date' : self.submit_date,
            'check_date' : self.check_date,
            'kra1_teacher' : self.kra1_teacher,
            'kra2_teacher' : self.kra2_teacher,
            'kra3_teacher' : self.kra3_teacher,
            'kra4_teacher' : self.kra4_teacher,
            'plus_factor_teacher' : self.plus_factor_teacher,
            'kra1_evaluator' : self.kra1_evaluator,
            'kra2_evaluator' : self.kra2_evaluator,
            'kra3_evaluator' : self.kra3_evaluator,
            'kra4_evaluator' : self.kra4_evaluator,
            'plus_factor_evaluator' : self.plus_factor_evaluator
        }
        
        # Find the evaluator
        if self.evaluator_id or self.evaluator_id != '':
            evaluator = People.objects.filter(is_deactivated = False, school_id=self.school_id, employee_id=self.evaluator_id).first()
            if evaluator:
                data['rater'] = evaluator.fullname
        
        # if self.form_type == 'PART 1':
        #     """
        #     {
        #         "1" : {
        #             "QUALITY" : "0",
        #             "EFFICIENCY" : "0",
        #             "TIMELINES" : "0",
        #             "Total" : "0"
        #         },
        #         "2" : {
        #             "QUALITY" : "0",
        #             "EFFICIENCY" : "0",
        #             "TIMELINES" : "0",
        #             "Total" : "0"
        #         },
        #     }
        #     """
        #     try : 
        #         for key in self.content_for_teacher:
        #             data[key] = {}
        #             total = 0
        #             if 'QUALITY' in self.content_for_teacher[key]:
        #                 quality_rate = self.content_for_teacher[key]['QUALITY']['Rate']
        #                 data[key]['QUALITY'] = quality_rate
        #                 total += int(quality_rate)
        #             if 'EFFICIENCY' in self.content_for_teacher[key]:
        #                 efficiency_rate = self.content_for_teacher[key]['EFFICIENCY']['Rate']
        #                 data[key]['EFFICIENCY'] = self.content_for_teacher[key]['EFFICIENCY']['Rate']
        #                 total += int(efficiency_rate)
        #             if 'TIMELINES' in self.content_for_teacher[key]:
        #                 timelines_rate = self.content_for_teacher[key]['TIMELINES']['Rate']
        #                 data[key]['TIMELINES'] = self.content_for_teacher[key]['TIMELINES']['Rate']
        #                 total += int(timelines_rate)
        #             data[key]['Total'] = total
        #     except Exception as e :
        #         data['Error'] = str(e)
        
        # if self.form_type == 'PART 2':
        #     pass
        #     # TODO : Add content for part 2

        
        # if self.form_type == 'PART 3':
        #     pass
        #     # TODO : Add content for part 3
        
        return data
    
    
    def getTeacherPart1Scores(self):
        """
        {
            '1' : {
                'QUALITY' : '0',
                'EFFICIENCY' : '0',
                'TIMELINES' : '0',
                'Total' : '0'
                'Average' : '0.0'
            },
            '2' : {
                'QUALITY' : '0',
                'EFFICIENCY' : '0',
                'TIMELINES' : '0',
                'Total' : '0',
                'Average' : '0.0'
            }
        }
        """
        # data = {}
        # content_for_teacher = self.content_for_teacher
        # if content_for_teacher:
        #     for key in content_for_teacher:
        #         data[key] = {}
        #         total = 0
        #         rates = []  # List of rates
                
        #         if 'QUALITY' in self.content_for_teacher[key]:
        #             quality_rate = self.content_for_teacher[key]['QUALITY']['Rate']
        #             data[key]['QUALITY'] = quality_rate
        #             total += int(quality_rate)
        #             rates.append(int(quality_rate))
                
        #         if 'EFFICIENCY' in self.content_for_teacher[key]:
        #             efficiency_rate = self.content_for_teacher[key]['EFFICIENCY']['Rate']
        #             data[key]['EFFICIENCY'] = self.content_for_teacher[key]['EFFICIENCY']['Rate']
        #             total += int(efficiency_rate)
        #             rates.append(int(efficiency_rate))
                
        #         if 'TIMELINES' in self.content_for_teacher[key]:
        #             timelines_rate = self.content_for_teacher[key]['TIMELINES']['Rate']
        #             data[key]['TIMELINES'] = self.content_for_teacher[key]['TIMELINES']['Rate']
        #             total += int(timelines_rate)
        #             rates.append(int(timelines_rate))
                
        #         data[key]['Total'] = total
        #         data[key]['Average'] = total / len(rates) if rates else 0  # Avoid division by zero

        # return data
        return {
            "rating" : self.rating if self.rating else 0,
            "average_score" : self.average_score if self.average_score else 0,
            "plus_factor" : self.plus_factor if self.plus_factor else 0
        }
    
    def getTeacherTotalAverage(self):
        if self.form_type == 'PART 1':
            return calculate_individual_averages_for_ipcrf(self.content_for_teacher)
        return None
        
        
    def getEvaluatorPart1Scores(self):
        """
        {
            'Content Knowledge and Pedagogy': {
                '1': {
                    'QUALITY': '5',
                    'EFFICIENCY': '3',
                    'TIMELINES': '4',
                    'Total': 12,
                    'Average': 4.0
                },
                '2': {
                    'QUALITY': '4',
                    'EFFICIENCY': '4',
                    'TIMELINES': '5',
                    'Total': 13,
                    'Average': 4.33
                }
                # Additional items as needed...
            },
            'Learning Environment & Diversity of Learners': {
                '5': {
                    'QUALITY': '3',
                    'EFFICIENCY': '5',
                    'TIMELINES': '4',
                    'Total': 12,
                    'Average': 4.0
                }
                # Additional items as needed...
            }
        }

        """        
        
        # data = {}
        # content_for_evaluator = self.content_for_evaluator
        # if content_for_evaluator:
        #     for key in content_for_evaluator:
        #         data[key] = {}
        #         total = 0
        #         rates = []  # List of rates
                
        #         if 'QUALITY' in self.content_for_evaluator[key]:
        #             quality_rate = self.content_for_evaluator[key]['QUALITY']['Rate']
        #             data[key]['QUALITY'] = quality_rate
        #             total += int(quality_rate)
        #             rates.append(int(quality_rate))
                
        #         if 'EFFICIENCY' in self.content_for_evaluator[key]:
        #             efficiency_rate = self.content_for_evaluator[key]['EFFICIENCY']['Rate']
        #             data[key]['EFFICIENCY'] = self.content_for_evaluator[key]['EFFICIENCY']['Rate']
        #             total += int(efficiency_rate)
        #             rates.append(int(efficiency_rate))
                
        #         if 'TIMELINES' in self.content_for_evaluator[key]:
        #             timelines_rate = self.content_for_evaluator[key]['TIMELINES']['Rate']
        #             data[key]['TIMELINES'] = self.content_for_evaluator[key]['TIMELINES']['Rate']
        #             total += int(timelines_rate)
        #             rates.append(int(timelines_rate))
                
        #         data[key]['Total'] = total
        #         data[key]['Average'] = total / len(rates) if rates else 0  # Avoid division by zero

        # return data
         
        average_score = self.evaluator_average_score if self.evaluator_average_score else 0
        plus_factor = self.evaluator_plus_factor if self.evaluator_plus_factor else 0
        rating = self.evaluator_rating if self.evaluator_rating else 0

        print(f"average_score: {average_score}, plus_factor: {plus_factor}, rating: {rating}")

        return {
            "average_score": average_score,
            "plus_factor": plus_factor,
            "rating": rating,
        }

    
    def getEvaluatorTotalAverage(self):
        if self.form_type == 'PART 1':
            return calculate_individual_averages_for_ipcrf(self.content_for_evaluator)
        return None
    

class COTForm(models.Model):
    """
        Form for evaluator to evaluate a teacher
    """
    school_id = models.CharField(max_length=255, blank=True, default='')
    employee_id = models.CharField(max_length=255, blank=True, default='') # ID of evaluator
    evaluated_id = models.CharField(max_length=255, blank=True, default='') # ID of teacher
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    school_year = models.CharField(max_length=255, blank=True, default='')
    
    status = models.CharField(max_length=255, blank=True, default='Pending',
        choices=(
         ('Pending', 'Pending'),
         ('Completed', 'Completed'),
        ))
    
    content = models.JSONField(default=dict, blank=True)
    """
        {
            "Observer ID" : "Evaluator ID",
            "Observer Name" : "Evaluator Name",
            "Teacher Name" : "Evaluated Name",
            "Teacher ID" : "Evaluated ID",
            "Subject & Grade Level" : "Subject & Grade 7",
            "Date : "September 05, 2023", !Save date after submiting,
            "Quarter": "1st Quarter",
            "Questions" : {
                "1" : {
                    "Objective" : "Applied knowledge of content within and across curriculum teaching areas. *",
                    "Selected" : "7" !Selected rate
                },
                "2" : {
                    "Objective" : "Applied knowledge of content within and across curriculum teaching areas. *",
                    "Selected" : "7" !Selected rate, kung "NO" means its "3"
                }
            },
            "Comments" : ""
        }
    """
    
    submit_date = models.DateTimeField(blank=True, null=True, default=None) 
    check_date = models.DateTimeField(blank=True, null=True, default=None)
    cot_form_id = models.CharField(max_length=255, blank=True, default='') # ID of COT
    is_checked = models.BooleanField(default=False)
    is_for_teacher_proficient = models.BooleanField(default=False) # If True, the folder is for teacher proffecient
    
    # New Added
    quarter = models.CharField(max_length=255, blank=True, default='') # Quarter 1, Quarter 2, Quarter 3, Quarter 4
    subject = models.CharField(max_length=255, blank=True, default='Not Assigned')

    strengths_prompt = models.TextField(blank=True, null=True, default='')
    weaknesses_prompt = models.TextField(blank=True, null=True, default='')
    opportunities_prompt = models.TextField(blank=True,null=True, default='')
    threats_prompt = models.TextField(blank=True, null=True, default='')



    def __str__(self):
        return f"{self.school_id} - {self.employee_id} - {self.evaluated_id} - {self.quarter} - {self.subject}"
    
   
    def get_information(self):
        
        data =  {
            'form' : 'COTForm',
            'school_id' : self.school_id,
            'employee_id' : self.employee_id,
            'created_at' : self.created_at,
            'content' : self.content,
            'status' : self.status,
            'cot_form_id' : self.cot_form_id,
            'is_checked' : self.is_checked,
            'is_for_teacher_proficient' : self.is_for_teacher_proficient,
            'quarter' : self.quarter,
            'evaluated_id' : self.evaluated_id,
            'rater' : None,
            'total' : 0 ,
            'subject' : self.subject,
            'school_year' : self.school_year,
            'submit_date' : self.submit_date,
            'check_date' : self.check_date
        }
        try:
            
            rater = People.objects.filter(is_deactivated = False, school_id=self.school_id, employee_id=self.employee_id).first()
            if rater:
                data['rater'] = rater.fullname
            
            
            if self.content:
                total = 0
                for key, values in self.content.items():
                    if key == 'Questions':
                        for question_key, question_values in values.items():
                            total += int(question_values['Selected'])
                
                data['total'] = total
                
        except Exception as e :
            data['Error'] = str(e)
        
        return data
    
    def getEvaluatorCOTScores(self):
        data = {}
        content = self.content
        total_scores = 0
        if content:
            if 'Questions' in content:
                for key, values in content['Questions'].items():
                    data[key] = {}
                    data[key]['Objective'] = values['Objective']
                    data[key]['Selected'] = values['Selected']
                
        return data
    
    def generatePromtTemplateNew(self): 
        all_promt = """
        The evaluation data has 'objective' and 'selected', OBJECTIVE is like a criteria that are being scored or rated, and the SELECTED is the score of the objective. 
	So base on the following evaluation data, what are the strengths? what are the weaknesses? what are the opportunities? what are the threats?
        For strengths, identify and summarize the key strengths of the teacher. 
	Focus on the indicators or objectives where the teacher has a high selected score (6, 7, or 8 ). And when the selected score of an objective is 3, 4, or 5, 
	do not include or remove it from the strengths. But do not copy the objectives directly. 
	Instead, provide a concise and insightful summary of the teacher's strengths, highlighting their positive attributes and effective teaching strategies. 
	Also, if all the objectives have a selected score of either 3, 4, or 5, the teacher shouldn't have strengths.
	Generate a summary of strengths, ensuring that the output is approximately 500 words or below in length in an essay form and it doesn't need to have a title, 
	but if there are no strengths, just say teacher has no strengths or other similar phrase.
	For weakness, identify and summarize the key weaknesses of the teacher. 
	Focus on the indicators or objectives where the teacher has a low selected score (3, 4, or 5). Use the objectives as a reference, and when the selected score of an objective is 6, 7, or 8, 
	do not include or remove it in weakness/es. But do not copy the objectives directly. 
	Instead, provide a concise and insightful summary of the teacher's areas for improvement, highlighting specific challenges or gaps in their teaching approach. 
	Also, if all the objectives have a selected score of either 6, 7, or 8, the teacher shouldn't have weakness.
	Generate a summary of weaknesses, ensuring that the output is approximately 500 words or below in length in an essay form and it doesn't need to have a title, 
	but if there are no weaknesses, just say teacher has no weaknesses or other similar phrase.
	For opportunities, basing on the strengths and weaknesses, generate a summary for opportunities, make it atleast 2-3 sentences and should not exceed 350 characters in total
        and only the sentences i need no need to add title or any additional information.
	For threats, basing on the strengths and weaknesses, generate a summary for threats, make it atleast 2-3 sentences and should not exceed 350 characters in total
        and only the sentences i need no need to add title or any additional information.
        Also if there are no data provided then tell that they did not take the "Individual Performance Commitment and Review Form"
        After generating convert it to a dictionary like this :
        {
            "strengths_prompt" : "Put the sentences here.",
            "weaknesses_prompt" : "Put the sentences here.",
            "opportunities_prompt" : "Put the sentences here.",
            "threats_prompt" : "Put the sentences here.",
        }
        Objectives and Ratings (0 - 7):
        """
        
        if self.content:
            if 'Questions' in self.content:
                questions = self.content['Questions']

                for q_id, q_info in questions.items():
                    all_promt += f"Objective: {q_info['Objective']} - Selected Rate: {q_info['Selected']}\n"

                if 'Comments' in self.content:
                    all_promt += "Comments: " + self.content["Comments"]
                    
        return all_promt
    def generatePromtTemplate(self):
        strengths_prompt = """
        Based on the following evaluation data,  identify and summarize the key strengths of the teacher. 
        Focus on the indicators where the teacher has received high ratings (6, 7, or 😎. Use the indicators as a reference, but do not copy them directly. 
        Instead, provide a concise and insightful summary of the teacher's strengths, highlighting their positive attributes and effective teaching strategies. 
        Generate a summarized list of strengths, ensuring that the output is approximately 500 words in length in an essay form and it doesn't need to have a title.
        Also if there are no data provided then tell that they did not take the "Individual Performance Commitment and Review Form"
        Objectives and Ratings (0 - 7):
        """

        weaknesses_prompt = """
        Based on the following evaluation data, identify and summarize the key weaknesses of the teacher. 
        Focus on the indicators where the teacher has received low ratings (3, 4, or 5). Use the indicators as a reference, but do not copy them directly. 
        Instead, provide a concise and insightful summary of the teacher's areas for improvement, highlighting specific challenges or gaps in their teaching approach. 
        Generate a summarized list of weaknesses, ensuring that the output is approximately 500 words in length in an essay form and it doesn't need to have a title.
        Also if there are no data provided then tell that they did not take the "Individual Performance Commitment and Review Form"
        Objectives and Ratings (0 - 7):
        """

        opportunities_prompt = """
        Based on the following evaluation data, what are the opportunities? Make it atleast 2-3 sentences and should not exceed 350 characters in total
        and only the sentences i need no need to add title or any additional information.
        Also if there are no data provided then tell that they did not take the "Individual Performance Commitment and Review Form"
        Objectives and Ratings (0 - 7):
        """

        threats_prompt = """
        Based on the following evaluation data, what are the threats? Make it atleast 2-3 sentences and should not exceed 350 characters in total
        and only the sentences i need no need to add title or any additional information.
        Also if there are no data provided then tell that they did not take the "Individual Performance Commitment and Review Form"
        Objectives and Ratings (0 - 7):
        """
        
        if self.content:
            if 'Questions' in self.content:
                questions = self.content['Questions']

                for q_id, q_info in questions.items():
                    strengths_prompt += f"Objective: {q_info['Objective']} - Selected Rate: {q_info['Selected']}\n"
                    weaknesses_prompt += f"Objective: {q_info['Objective']} - Selected Rate: {q_info['Selected']}\n"
                    opportunities_prompt += f"Objective: {q_info['Objective']} - Selected Rate: {q_info['Selected']}\n"
                    threats_prompt += f"Objective: {q_info['Objective']} - Selected Rate: {q_info['Selected']}\n"
                    
                if 'Comments' in self.content:
                    strengths_prompt += "Comments: " + self.content["Comments"]
                    weaknesses_prompt += "Comments: " + self.content["Comments"]
                    opportunities_prompt += "Comments: " + self.content["Comments"]
                    threats_prompt += "Comments: " + self.content["Comments"]

        return {
            'strengths' : strengths_prompt,
            'weaknesses' : weaknesses_prompt,
            'opportunities' : opportunities_prompt,
            'threats' : threats_prompt
        }

    def getOldAIPromt(self):
        return {
            'strengths' : self.strengths_prompt,
            'weaknesses' : self.weaknesses_prompt,
            'opportunities' : self.opportunities_prompt,
            'threats' : self.threats_prompt
        }
    
    def isAlreadyAIGenerated(self):
        if not self.strengths_prompt:
            return False
        
        if len(self.strengths_prompt) > 0:
            return True
        return False
        
        
class RPMSFolder(models.Model):
    """_summary_
    A class to represent a folder in the RPMS system. Created by Head Administrator.
    This is where the RPMS class work is created and located
    
    Args:
        models (_type_): _description_
    """
    school_id = models.CharField(max_length=255, blank=True, default='') # Identify what school created this folder
    employee_id = models.CharField(max_length=255, blank=True, default='') # I don't know where to use it, but just stay there
    
    
    rpms_folder_name = models.CharField(max_length=255, blank=True, default='') # Name of the folder
    rpms_folder_school_year = models.CharField(max_length=255, blank=True, default='') # School Year of the folder
    is_for_teacher_proficient = models.BooleanField(default=False) # If True, the folder is for teacher proffecient
    
    background_image = models.ImageField(upload_to='rpms_folders/', blank=True, null=True) # Background image of the folder
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    rpms_folder_id = models.CharField(max_length=255, blank=True, default='') # Unique ID of the folder
    rpms_folder_color = models.CharField(max_length=255, blank=True, default='') # Color of the folder
    rpms_folder_background_color = models.CharField(max_length=255, blank=True, default='') # Background Color of the folder
    
    def __str__(self):
        return f"{self.school_id} - {self.rpms_folder_name} - {'Proficient' if self.is_for_teacher_proficient else 'Highly Proficient'} - {self.rpms_folder_school_year} - {self.employee_id} - {self.rpms_folder_id}"
    
    
    def get_rpms_folder_information(self):
        data =  {  
            'rpms_folder_name' : self.rpms_folder_name,
            'rpms_folder_school_year' : self.rpms_folder_school_year,
            'rpms_folder_id' : self.rpms_folder_id,
            'rpms_folder_background' : None ,
            'is_for_teacher_proficient' : self.is_for_teacher_proficient,
            'rpms_folder_color' : self.rpms_folder_color,
            'rpms_folder_background_color' : self.rpms_folder_background_color,
            'rpms_folder_created_at' : self.created_at,
            'school_id' : self.school_id
        }
        
        if self.background_image:
            data['rpms_folder_background'] = self.background_image.url
        
        return data
    

class RPMSClassWork(models.Model):
    """_summary_

        A class to represent a classwork created by Head Adminstrator. 
        This where the RPMS Attachement is uploaded.
    """
    school_id = models.CharField(max_length=255, blank=True, default='') # Identify what school
    employee_id = models.CharField(max_length=255, blank=True, default='') # I don't know where to use it, but just stay there
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    school_year = models.CharField(max_length=255, blank=True, default='') # School Year of the classwork
    rpms_folder_id = models.CharField(max_length=255, blank=True, default='')
    class_work_id = models.CharField(max_length=255, blank=True, default='') # id of the class work
    
    due_date = models.DateTimeField(blank=True, null=True)
    
    title = models.CharField(max_length=255, blank=True, default='')
    objectives = models.JSONField(default=dict, blank=True)
    """
        {
            "Instructions" : {
                "Title" : "KRA 1: Content Knowledge and Pedagogy", 
                "Date" : "dsfsdf",
                "Time" : "6:01 PM",
                "Points" : "28 points" ,
                "Objectives" : {
                    "1" : {
                        "Main Title" : "7% | Objective 1 (Applied knowledge of content within and across curriculum teaching areas)",
                        "Title" : "Means of Verification (MOV)",
                        "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter-observer agreement form/s"
                    },
                    "2" : {
                        "Main Title" : "7% | Objective 1 (Applied knowledge of content within and across curriculum teaching areas)",
                        "Title" : "Means of Verification (MOV)",
                        "Bullet" : "Classroom Observation Tool (COT) rating sheet/s or inter-observer agreement form/s"
                    }
                }
            },
            "Grade" : {
                "1" : {
                    "Content" : "KRA 1: Content Knowledge and Pedagogy",
                    "Score" : "5",
                    "Maximum Score" : "7",
                },
                "2" : {
                    "Content" : "KRA 1: Content Knowledge and Pedagogy",
                    "Score" : "5"
                    "Maximum Score" : "7",
                }
            },
            "Comment" : " "
        }
    """

    def __str__(self):
        return f"{self.rpms_folder_id} - {self.class_work_id} - {self.created_at}"

    def get_rpms_classwork_information(self , attachment = None):
        data = {
            'rpms_folder_id' : self.rpms_folder_id,
            'class_work_id' : self.class_work_id,
            'title' : self.title,
            'objectives' : self.objectives,
            'due_date' : self.due_date,
            'created_at' : self.created_at
        }
        # attachment = RPMSAttachment.objects.filter(class_work_id=self.class_work_id).order_by('-created_at').first()
        data["attachment"] = attachment.get_information() if attachment else None
        return data

    def get_grade(self):
        
        return self.objectives.get('Grade', {})
     

class RPMSAttachment(models.Model):
    """
        A class to represent a attachment in the RPMS Classwork.
        This is uploaded to the RPMS Classwork.
    
    """
    
    school_id = models.CharField(max_length=255, blank=True, default='')
    employee_id = models.CharField(max_length=255, blank=True, default='')
    evaluator_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class_work_id = models.CharField(max_length=255, blank=True, default='')
    
    status = models.CharField(max_length=255, blank=True, default='Pending',
        choices=(
         ('Pending', 'Pending'),
         ('Approved', 'Approved'),
         ('Rejected', 'Rejected'),
         ('Cancelled', 'Cancelled'),
         ('Completed', 'Completed'),
        ))
    
    attachment_id = models.CharField(max_length=255, blank=True, default='')
    streams_type = models.CharField(max_length=255, blank=True, default='', 
        choices=(
         ('Pending', 'Pending'),
         ('Approved', 'Approved'),
         ('Rejected', 'Rejected'),
         ('Cancelled', 'Cancelled'),
         ('Completed', 'Completed'),
        ))
    
    title = models.CharField(max_length=255, blank=True, default='') # Name of classwork
    file = models.FileField(upload_to='rpms_attachments' , blank=True, null=True) # Objectives 1 
    file_is_checked = models.BooleanField(default=False) 
    file2 = models.FileField(upload_to='rpms_attachments' , blank=True, null=True) # Objectives 2
    file2_is_checked = models.BooleanField(default=False) 
    file3 = models.FileField(upload_to='rpms_attachments' , blank=True, null=True) # Objectives 3
    file3_is_checked = models.BooleanField(default=False) 
    file4 = models.FileField(upload_to='rpms_attachments' , blank=True, null=True) # Objectives 4
    file4_is_checked = models.BooleanField(default=False) 
    
    grade : dict[str, dict] = models.JSONField(default=dict, blank=True)
    """
        {
            "1" : {
                "Content" : "KRA 1: Content Knowledge and Pedagogy",
                "Score" : "5",
                "Maximum Score" : "7",
            },
            "2" : {
                "Content" : "KRA 1: Content Knowledge and Pedagogy",
                "Score" : "5"
                "Maximum Score" : "7",
            }
        }
    """
    
    is_checked = models.BooleanField(default=False) 
    is_for_teacher_proficient = models.BooleanField(default=False) 
    school_year = models.CharField(max_length=255, blank=True, default='')
    
    check_date = models.DateTimeField(blank=True, null=True, default=None) # Objective 1
    submit_date = models.DateTimeField(blank=True, null=True, default=None) # Objective 1

    is_submitted = models.BooleanField(default=False) # Used to identify if submitted
    post_id = models.CharField(max_length=255, blank=True, default='') # Used to identify the comment 
    
    teacher_comment = models.TextField(blank=True, default='')
    comment_1 = models.TextField(blank=True, default='')
    comment_2 = models.TextField(blank=True, default='')
    comment_3 = models.TextField(blank=True, default='')
    comment_4 = models.TextField(blank=True, default='')
    teacher_comments : list = models.JSONField(default=list, blank=True)
    """
        {'comment' : comment, 'date' : str(timezone.now()) , 'role' : 'Teacher'}
    """
    
    def __str__(self):
        return f"{self.class_work_id} - {self.employee_id} - {self.evaluator_id} - {self.attachment_id}" 
    
    
    def get_information(self):
        data =  {
            'form' : 'RPMSAttachment',
            'school_id' : self.school_id,
            'employee_id' : self.employee_id,
            'created_at' : self.created_at,
            'class_work_id' : self.class_work_id,
            'status' : self.status,
            'attachment_id' : self.attachment_id,
            'streams_type' : self.streams_type,
            'title' : self.title,
            'grade' : self.grade,
            'is_checked' : self.is_checked,
            "post_id" : self.post_id,
            'is_submitted' : self.is_submitted,
            'comment' : None,
            'submit_date' : self.submit_date,
            'check_date' : self.check_date,
            'file_is_checked' : self.file_is_checked,
            'file2_is_checked' : self.file2_is_checked,
            'file3_is_checked' : self.file3_is_checked,
            'file4_is_checked' : self.file4_is_checked,
            'teacher_comment' : self.teacher_comment,
            'comment_1' : self.comment_1,
            'comment_2' : self.comment_2,
            'comment_3' : self.comment_3,
            'comment_4' : self.comment_4,
            'teacher_comments' : self.teacher_comments
        }
        """
        {
            "1" : {
                "Score" : "5"
            },
            "2" : {
                "Score" : "5"
            }
        }
        
        """
        try:
            
            comment = Comment.objects.filter(post_id=self.post_id).first()
            if comment:
                data['comment'] = comment.get_comment()

            
            data['file'] = self.file.url if self.file else None
            data['file2'] = self.file2.url if self.file2 else None
            data['file3'] = self.file3.url if self.file3 else None
            data['file4'] = self.file4.url if self.file4 else None
            
            
            overall_score = 0
            if self.grade:
                for key, value in self.grade.items():
                    total = 0
                    data[key] = {}
                    for subkey, subvalue in value.items():
                        if subkey == 'Score':
                            data[key][subkey] = subvalue
                            total += int(subvalue)
                    data[key]['Total'] = total
                    overall_score += total
            data['Overall Score'] = overall_score
        except Exception as e:
            data['error'] = str(e)
        
        
        
        return data

    def getGradeSummary(self) -> dict:
        
        data = {
            'Title': self.title,
            'Total': 0,
            'Average': 0
        }

        total = 0
        number_of_scores = 0

        for key, value in self.grade.items():
            for subkey, subvalue in value.items():
                if subkey == 'Score':
                    try:
                        total += int(subvalue)
                        number_of_scores += 1
                    except ValueError:
                        # print(f"Non-numeric score encountered: {subvalue}")
                        continue

        data['Total'] = total

        # Check to prevent division by zero
        if number_of_scores > 0:
            data['Average'] = total / number_of_scores
        else:
            data['Average'] = 0  # or you can keep it as the initialized value

        return data

 

class MainAdmin(models.Model):
    
    username = models.CharField(max_length=255, blank=True, default='')
    password = models.CharField(max_length=255, blank=True, default='')
    
    role = models.CharField(max_length=10, blank=True, default='ADMIN')
    action_id = models.CharField(max_length=255, blank=True, default='') # Used to track actions ( 'Posts' , 'Comments' , 'Replies' )
    
#     # total school
#     # total teacher
#     # number of forms answered

    def __str__(self):
        return f"{self.username} - {self.password}"

    
    
class School(models.Model):
    
    name = models.CharField(max_length=255 , blank=True, default='')
    school_id = models.CharField(max_length=255, blank=True, default='')
    school_name = models.CharField(max_length=255, blank=True, default='')
    school_address = models.CharField(max_length=255, blank=True, default='')
    school_type = models.CharField(max_length=255, choices=(('Urban', 'Urban'), ('Rural', 'Rural')) , blank=True, default='')
    contact_number = models.CharField(max_length=255, blank=True, default='')
    email_address = models.CharField(max_length=255, blank=True, default='')
    password = models.CharField(max_length=255, blank=True, default='')
    confirm_password = models.CharField(max_length=255, blank=True, default='')
    school_logo = models.ImageField(upload_to='school_logo', blank=True, null=True)
    
    # number of forms answered / evaluation submision rate
    
    is_declined = models.BooleanField(default=False) # is the school declined
    is_verified = models.BooleanField(default=False) # Is the school verified or click the link
    is_accepted = models.BooleanField(default=False) # Is the school accepted or added by admin
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    reason = models.TextField( blank=True, default='Other')
    action_id = models.CharField(max_length=255, blank=True, default='') # Used to track actions ( 'Posts' , 'Comments' , 'Replies' )

    def __str__(self):
        return f"{self.name} - {self.school_id} - {self.email_address} - {self.contact_number} - Verified : {self.is_verified} - Accepted : {self.is_accepted} - Declined : {self.is_declined}"
    
    def get_school_information(self):
        
        school = {
            'name' : self.name,
            'school_id' : self.school_id,
            'school_name' : self.school_name,
            'school_address' : self.school_address,
            'school_type' : self.school_type,
            'contact_number' : self.contact_number,
            'email_address' : self.email_address,
            'school_logo' : '',
            'is_accepted' : self.is_accepted,
            'is_verified' : self.is_verified,
            'is_declined' : self.is_declined,
            'role' : 'School Admin',
            'reason' : self.reason,
            'action_id' : self.action_id
        }
        
        if self.school_logo:
            if self.school_logo.url:
                school['school_logo'] = self.school_logo.url
    
        return school
        

    
class People(models.Model):
    role = models.CharField(max_length=255, choices=(
        ('Evaluator', 'Evaluator'), 
        ('Teacher', 'Teacher')) , 
    blank=True, default='') # What the person does
    school_id = models.CharField(max_length=255, blank=True, default='') # Where school the person belongs
    
    # ratings = models.IntegerField(default=0)
    # recomendation
    # work_start = models.DateTimeField(blank=True, null=True)
    # work_end = models.DateTimeField(blank=True, null=True)
    
    employee_id = models.CharField(max_length=255, blank=True, default='')
    first_name = models.CharField(max_length=255, blank=True, default='')
    middle_name = models.CharField(max_length=255, blank=True, default='')
    last_name = models.CharField(max_length=255, blank=True, default='')
    email_address = models.CharField(max_length=255, blank=True, default='')
    position = models.CharField(max_length=255, blank=True, default='')
    job_started = models.DateTimeField(blank=True, null=True)
    job_ended = models.DateTimeField(blank=True, null=True)
    
    grade_level = models.CharField(max_length=255, blank=True, default='')
    department = models.CharField(max_length=255, blank=True, default='')
    password = models.CharField(max_length=255, blank=True, default='')
    confirm_password = models.CharField(max_length=255, blank=True, default='')
    
    
    fullname = models.CharField(max_length=255, blank=True, default='') 
    school_action_id = models.CharField(max_length=255, blank=True, default='') # Used to track actions ( 'Posts' , 'Comments' , 'Replies' )
    action_id = models.CharField(max_length=255, blank=True, default='') # Used to track actions ( 'Posts' , 'Comments' , 'Replies' )
    
    educations = models.JSONField(default=list, blank=True)
    """
        educations = [
            {
                'degree' : '',
                'university' : ''
            }
        ]
    """
    
    is_evaluated = models.BooleanField(default=False) # Is the person evaluated or not
    is_deactivated = models.BooleanField(default=False) # Is the person deactivated or not
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    reason = models.CharField(max_length=255, blank=True, default='Other') # is the school declined and reason
    is_declined = models.BooleanField(default=False) # is the school declined
    is_verified = models.BooleanField(default=False) # Is the school verified or click the link
    is_accepted = models.BooleanField(default=False) # Is the school accepted or added by admin
    
    profile = models.ImageField(upload_to='profile/', blank=True, default='')
    
    def __str__(self):
        return f"{self.role} : {self.first_name} {self.last_name} - {self.employee_id} - {self.school_id} - {self.email_address} - {self.position} - {self.department}"

    def save(self, *args, **kwargs):
        self.fullname = f"{self.first_name} {self.middle_name} {self.last_name}"
        super().save(*args, **kwargs)
    
    def get_information(self):
        data = {
            'role' : self.role,
            'school_id' : self.school_id,
            'employee_id' : self.employee_id,
            'first_name' : self.first_name,
            'middle_name' : self.middle_name,
            'last_name' : self.last_name,
            'email_address' : self.email_address,
            'position' : self.position,
            'job_started' : self.job_started,
            'job_ended' : self.job_ended,
            'grade_level' : self.grade_level,
            'department' : self.department,
            'is_evaluated' : self.is_evaluated,
            'is_deactivated' : self.is_deactivated,
            'created_at' : self.created_at,
            'is_declined' : self.is_declined,
            'is_verified' : self.is_verified,
            'is_accepted' : self.is_accepted,
            'fullname' : self.fullname,
            'action_id' : self.action_id,
            'educations' : self.educations,
            'profile' : '',
            'reason' : self.reason
        }
        
        ipcrf = IPCRFForm.objects.filter(school_id=self.school_id , employee_id=self.employee_id).first()
        if ipcrf:
            data['is_checked'] = ipcrf.is_checked
            data['is_checked_by_evaluator'] = ipcrf.is_checked_by_evaluator
            if ipcrf.is_checked_by_evaluator:
                rater = People.objects.filter(is_deactivated = False, employee_id=ipcrf.evaluator_id).first()
                if rater:
                    data['evaluator'] = rater.get_information()
        
        if self.role == "Teacher":
            data['is_proficient'] = is_proficient_faculty_teacher_in_model(self.position)
        else :
            data['is_proficient'] = is_proficient_faculty_evaluator_in_model(self.position)
            
        if self.profile:
            data['profile'] = self.profile.url
        
        return data
    
    def working_years(self):
        if self.job_ended:
            year_gap = self.job_ended.year - self.job_started.year - ((self.job_ended.month, self.job_ended.day) < (self.job_started.month, self.job_started.day))
            return year_gap

        if self.job_started:
            now = timezone.now()
            year_gap = now.year - self.job_started.year - ((now.month, now.day) < (self.job_started.month, self.job_started.day))
            return year_gap
        
        return 0
    
    def get_tenure_category(self):
        if self.working_years() <= 3:
            return '0-3 years'
        elif self.working_years() <= 5:
            return '3-5 years'
        else:
            return '5+ years'
    
    
    def update_educations(self, data):
        self.educations = data
        self.save()
    

    def get_name_and_action_id(self):
        return {
            'name' : f"{self.first_name} {self.middle_name} {self.last_name}",
            'id' : self.action_id,
        }
    
    
    def get_form_status(self):
        data = {}
        
        part_1 = IPCRFForm.objects.filter(employee_id=self.employee_id, form_type='PART 1').first() 
        
        data['part_1'] = part_1.is_checked
        
        number_of_attachment_evaluated = 1 
        attachments = RPMSAttachment.objects.filter(employee_id=self.employee_id)
        for attachment in attachments:
            data[attachment.title] = attachment.is_checked
            if attachment.is_checked :
                number_of_attachment_evaluated += 1
        
        data['evaluated'] = True if number_of_attachment_evaluated == 6 else False
        
        return data
         

    def get_job_years(self):
        now = timezone.now()
        difference = relativedelta(now, self.job_started)

        years = difference.years
        months = difference.months
        days = difference.days

        return {
            "years": years,
            "months": months,
            "days": days
        }

        

    def update_is_evaluted(self , school_year = None):
        cot_1 = COTForm.objects.filter(evaluated_id=self.employee_id, quarter="Quarter 1").order_by('-created_at').first()
        cot_2 = COTForm.objects.filter(evaluated_id=self.employee_id, quarter="Quarter 2").order_by('-created_at').first()
        cot_3 = COTForm.objects.filter(evaluated_id=self.employee_id, quarter="Quarter 3").order_by('-created_at').first()
        cot_4 = COTForm.objects.filter(evaluated_id=self.employee_id, quarter="Quarter 4").order_by('-created_at').first()
        
        if cot_1 and cot_2 and cot_3 and cot_4:
            if all([cot_1.is_checked, cot_2.is_checked, cot_3.is_checked, cot_4.is_checked]):
                pass
            else:
                return "Evaluator not fully checked Quarter 1, Quarter 2, Quarter 3 and Quarter 4 in Rating Sheet."
        else:
            return "Quarter 1, Quarter 2, Quarter 3 and Quarter 4 in Rating Sheet does not exist."
        
        folder = RPMSFolder.objects.filter(school_id=self.school_id , is_for_teacher_proficient=is_proficient_faculty_teacher_in_model(self.role)).order_by('-created_at').first()
        if not folder:
            return "No Folder found in Results-Based Performance Management System"
        
        classworks = RPMSClassWork.objects.filter(rpms_folder_id=folder.rpms_folder_id).order_by('-created_at')
        if not classworks:
            return "No Classes Found in Results-Based Performance Management System"
        
        
        for classwork in classworks:
            attachment = RPMSAttachment.objects.filter(class_work_id=classwork.class_work_id).order_by('-created_at').first()
            if not attachment:
                return "No Attachments Found in Results-Based Performance Management System or Incomplete Attachment"

            if not attachment.is_checked:
                return "Attachment in Results-Based Performance Management System not fully checked"
            
        
        ipcrf_1 = IPCRFForm.objects.filter( school_id=self.school_id , employee_id=self.employee_id , form_type="PART 1").order_by('-created_at').first()
        if not ipcrf_1:
            return "Individual Performance Commitment Review Form Part 1 does not exist."
        
        if not ipcrf_1.is_checked:
            return "Individual Performance Commitment Review Form Part 1 not fully checked"
        
        if not ipcrf_1.is_checked_by_evaluator:
            return "Individual Performance Commitment Review Form Part 1 not fully checked by evaluator"
        
        ipcrf_2 = IPCRFForm.objects.filter( school_id=self.school_id , employee_id=self.employee_id , form_type="PART 2").order_by('-created_at').first()
        if not ipcrf_2:
            return "Individual Performance Commitment Review Form Part 2 does not exist."
        
        if not ipcrf_2.is_checked:
            return "Individual Performance Commitment Review Form Part 2 not fully checked" 
        
        ipcrf_3 = IPCRFForm.objects.filter( school_id=self.school_id , employee_id=self.employee_id , form_type="PART 3").order_by('-created_at').first()
        if not ipcrf_3:
            return "Individual Performance Commitment Review Form Part 3 does not exist."
        
        if not ipcrf_3.is_checked:
            return "Individual Performance Commitment Review Form Part 3 not fully checked" 
        
        
        self.is_evaluated = True
        self.save()
        return "Teacher is Evaluated."
    
    
    def get_recent_ipcrf_score(self):
        # Get the most recent IPCRF form by the creation date
        recent_form = IPCRFForm.objects.filter(employee_id=self.employee_id, form_type='PART 1', is_expired=False).order_by('-created_at').first()
        if recent_form:
            # Assuming the form has a method to get the average score
            scores = recent_form.getEvaluatorPart1Scores()
            # Calculate the overall average from the scores
            # total_score = 0
            # count = 0
            # for key, value in scores.items():
            #     total_score += value['Average']
            #     count += 1
            # if count > 0:
            #     return total_score / count
            return scores["average_score"] if scores else 0
        return 0  # Return None if no recent form is found


    def get_rpms_attachments_by_folder_id(self , folder_id : str ):
        classworks = RPMSClassWork.objects.filter(rpms_folder_id=folder_id).order_by('-created_at')
        data = {}
        
        for classwork in classworks: 
            attachments = RPMSAttachment.objects.filter(school_id=classwork.school_id ,class_work_id=classwork.class_work_id).order_by('-created_at')
            data[classwork.title] = [ attachment for attachment in attachments ]
        
        return data

    
# 1. title and scores for KBA BREAKDOWN
# 2. rule based classifier for Promotion
# 3. date of submission and score Performance tru year
# 4. generated text SWOT from COTForm 
