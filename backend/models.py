from django.db import models 
from django.conf import settings
from django.utils import timezone

import uuid, string ,random
# Create your models here.


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




class Post(models.Model):
    post_owner = models.CharField(max_length=255, blank=True, default='') # Action ID of owner of post
    content = models.TextField(blank=True, default='') # Content of post
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    post_id = models.CharField(max_length=255, blank=True, default='') # Generated id by system to identify post
    liked = models.JSONField(default=list, blank=True)
    """
        liked = [
            action_id,
            action_id,
        ]
    """
    
    commented = models.JSONField(default=list, blank=True)
    """
        commented = [
            action_id,
            action_id,
        ]
    """
    
    mentions = models.JSONField(default=list, blank=True)
    """
        mentions = [
            action_id,
            action_id,
        ]
    """
    
    
    def __str__(self):
        return f"{self.post_owner} - {self.post_id}"
    
    
    def get_post(self, action_id = None):
        data = {
            'post_owner' : self.post_owner,
            'content' : self.content,
            'created_at' : self.created_at,
            'number_of_likes' : 0,
            'liked' : False,
            'commented' : False,
            'created_at' : self.created_at
        }
        
        if self.liked:
            data['number_of_likes'] = len(self.liked)
        
        if action_id:
            if action_id in self.liked:
                data['liked'] = True
            if action_id in self.commented:
                data['commented'] = True
        
        return data
        
           

class PostAttachment(models.Model):
    ppst_owner = models.CharField(max_length=255, blank=True, default='')
    post_id = models.CharField(max_length=255, blank=True, default='')
    attachment = models.FileField(upload_to='uploads/', default='', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    def __str__(self):
        return f"{self.post_id} - {self.attachment}"

    def get_attachment(self):
        return {
            'attachment' : self.attachment.url if self.attachment else '',
            'created_at' : self.created_at,
        }
    

class Comment(models.Model):
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    post_id = models.CharField(max_length=255, blank=True, default='') # post_id of post where comment is posted
    comment_owner = models.CharField(max_length=255, blank=True, default='') # Action ID of owner of comment

    replied_to = models.CharField(max_length=255, blank=True, default='') # Action ID where comment is replied
    is_seen = models.JSONField(default=list, blank=True)
    """
        is_seen = [
            action_id,
            action_id,
        ]
    """ 
    
    def __str__(self):
        return f"{self.comment_owner} - {self.post_id}"
    
    def get_comment(self , action_id = None):
        data = {
            'content' : self.content,
            'created_at' : self.created_at,
            'post_id' : self.post_id,
            'comment_owner' : self.comment_owner,
            'replied_to' : self.replied_to,
            'attachment' : '',
            'created_at' : self.created_at,
        }
        
        if self.attachment or self.attachment != "":
            data['attachment'] = self.attachment.url
        
        if action_id:
            if action_id in self.is_seen:
                data['is_seen'] = True 
        
        return data
    
    
    def update_is_seen(self, action_id):
        if action_id not in self.is_seen:
            self.is_seen.append(action_id)
            self.save()
    
    def is_seen(self, action_id):
        """
            Returns True if action_id == replied_to
            Returns False if action_id != replied_to
            
            Returns None if action_id is not in is_seen
            Returns boolean if action_id is in is_seen
        """
        if action_id != self.replied_to:
            return (False, None)
        return ( True, action_id in self.is_seen)


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
    
    rating = models.FloatField( blank=True, default=0.0) # Rating
    average_score = models.FloatField( blank=True, default=0.0) # Average Score
    plus_factor = models.FloatField( blank=True, default=0.0) # Plus Factor Score
    
    def __str__(self):
        return f"{self.school_id} - {self.employee_id} - {self.created_at}"
    
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
        }
        
        # Find the evaluator
        # if self.evaluator_id or self.evaluator_id != '':
        #     evaluator = People.objects.filter(school_id=self.school_id, employee_id=self.evaluator_id).first()
        #     if evaluator:
        #         data['evaluator'] = evaluator.get_information()
        
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
        data = {}
        content_for_teacher = self.content_for_teacher
        if content_for_teacher:
            for key in content_for_teacher:
                data[key] = {}
                total = 0
                rates = []  # List of rates
                
                if 'QUALITY' in self.content_for_teacher[key]:
                    quality_rate = self.content_for_teacher[key]['QUALITY']['Rate']
                    data[key]['QUALITY'] = quality_rate
                    total += int(quality_rate)
                    rates.append(int(quality_rate))
                
                if 'EFFICIENCY' in self.content_for_teacher[key]:
                    efficiency_rate = self.content_for_teacher[key]['EFFICIENCY']['Rate']
                    data[key]['EFFICIENCY'] = self.content_for_teacher[key]['EFFICIENCY']['Rate']
                    total += int(efficiency_rate)
                    rates.append(int(efficiency_rate))
                
                if 'TIMELINES' in self.content_for_teacher[key]:
                    timelines_rate = self.content_for_teacher[key]['TIMELINES']['Rate']
                    data[key]['TIMELINES'] = self.content_for_teacher[key]['TIMELINES']['Rate']
                    total += int(timelines_rate)
                    rates.append(int(timelines_rate))
                
                data[key]['Total'] = total
                data[key]['Average'] = total / len(rates) if rates else 0  # Avoid division by zero

        return data
    
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
        
        data = {}
        content_for_evaluator = self.content_for_evaluator
        if content_for_evaluator:
            for key in content_for_evaluator:
                data[key] = {}
                total = 0
                rates = []  # List of rates
                
                if 'QUALITY' in self.content_for_evaluator[key]:
                    quality_rate = self.content_for_evaluator[key]['QUALITY']['Rate']
                    data[key]['QUALITY'] = quality_rate
                    total += int(quality_rate)
                    rates.append(int(quality_rate))
                
                if 'EFFICIENCY' in self.content_for_evaluator[key]:
                    efficiency_rate = self.content_for_evaluator[key]['EFFICIENCY']['Rate']
                    data[key]['EFFICIENCY'] = self.content_for_evaluator[key]['EFFICIENCY']['Rate']
                    total += int(efficiency_rate)
                    rates.append(int(efficiency_rate))
                
                if 'TIMELINES' in self.content_for_evaluator[key]:
                    timelines_rate = self.content_for_evaluator[key]['TIMELINES']['Rate']
                    data[key]['TIMELINES'] = self.content_for_evaluator[key]['TIMELINES']['Rate']
                    total += int(timelines_rate)
                    rates.append(int(timelines_rate))
                
                data[key]['Total'] = total
                data[key]['Average'] = total / len(rates) if rates else 0  # Avoid division by zero

        return data
    
    
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
    
    cot_form_id = models.CharField(max_length=255, blank=True, default='') # ID of COT
    is_checked = models.BooleanField(default=False)
    is_for_teacher_proficient = models.BooleanField(default=False) # If True, the folder is for teacher proffecient
    
    # New Added
    quarter = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f"{self.school_id} - {self.employee_id} - {self.created_at}"
    
   
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
            'is_for_teacher_proficient' : self.is_for_teacher_proficient
        }
        try:
            if self.content:
                total = 0
                for key, values in self.content.items():
                    if key == 'Questions':
                        for question_key, question_values in values.items():
                            total += int(question_values['Selected'])
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
    
    def generatePromtTemplate(self):
        strengths_prompt = """
        Based on the following evaluation data, 
        what are the strengths? Make it atleast 2-3 sentences 
        and only the sentences i need no need to add title or any additional information.
        Also if there are no data provided then tell that they did not take the "Individual Performance Commitment and Review Form"
        Objectives and Ratings:
        """

        weaknesses_prompt = """
        Based on the following evaluation data, what are the weaknesses? Make it atleast 2-3 sentences
        and only the sentences i need no need to add title or any additional information.
        Also if there are no data provided then tell that they did not take the "Individual Performance Commitment and Review Form"
        Objectives and Ratings:
        """

        opportunities_prompt = """
        Based on the following evaluation data, what are the opportunities? Make it atleast 2-3 sentences
        and only the sentences i need no need to add title or any additional information.
        Also if there are no data provided then tell that they did not take the "Individual Performance Commitment and Review Form"
        Objectives and Ratings:
        """

        threats_prompt = """
        Based on the following evaluation data, what are the threats? Make it atleast 2-3 sentences
        and only the sentences i need no need to add title or any additional information.
        Also if there are no data provided then tell that they did not take the "Individual Performance Commitment and Review Form"
        Objectives and Ratings:
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


class RPMSFolder(models.Model):
    """_summary_
    A class to represent a folder in the RPMS system. Created by Head Administrator.
    This is where the RPMS class work is created and located
    
    Args:
        models (_type_): _description_
    """
    school_id = models.CharField(max_length=255, blank=True, default='') # I don't know where to use it, but just stay there
    employee_id = models.CharField(max_length=255, blank=True, default='') # I don't know where to use it, but just stay there
    
    
    rpms_folder_name = models.CharField(max_length=255, blank=True, default='') # Name of the folder
    rpms_folder_school_year = models.CharField(max_length=255, blank=True, default='') # School Year of the folder
    is_for_teacher_proficient = models.BooleanField(default=False) # If True, the folder is for teacher proffecient
    
    background_image = models.ImageField(upload_to='rpms_folders/', blank=True, null=True) # Background image of the folder
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    rpms_folder_id = models.CharField(max_length=255, blank=True, default='') # Unique ID of the folder
    
    def __str__(self):
        return f"{self.school_id} - {self.employee_id} - {self.created_at}"
    
    
    def get_rpms_folder_information(self):
        data =  {  
            'rpms_folder_name' : self.rpms_folder_name,
            'rpms_folder_school_year' : self.rpms_folder_school_year,
            'rpms_folder_id' : self.rpms_folder_id,
            'rpms_folder_background' : '' ,
            'is_for_teacher_proficient' : self.is_for_teacher_proficient
        }
        
        if self.background_image is not None:
            data['rpms_folder_background'] = self.background_image.url
        
        return data
    

class RPMSClassWork(models.Model):
    """_summary_

        A class to represent a classwork created by Head Adminstrator. 
        This where the RPMS Attachement is uploaded.
    """
    school_id = models.CharField(max_length=255, blank=True, default='') # I don't know where to use it, but just stay there
    employee_id = models.CharField(max_length=255, blank=True, default='') # I don't know where to use it, but just stay there
    
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    
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
        return f"{self.school_id} - {self.employee_id} - {self.created_at}"

    def get_rpms_classwork_information(self):
        return {
            'rpms_folder_id' : self.rpms_folder_id,
            'class_work_id' : self.class_work_id,
            'title' : self.title,
            'objectives' : self.objectives,
            'due_date' : self.due_date,
            'created_at' : self.created_at,
        }

    def get_grade(self):
        return self.objectives.get('Grade', '')

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
    file = models.FileField(upload_to='rpms_attachments' , blank=True, null=True)
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
    def __str__(self):
        return f"{self.school_id} - {self.employee_id} - {self.created_at}"
    
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
            'is_checked' : self.is_checked
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
            data['file'] = self.file.url if self.file else None
            
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
            pass
        
        
        
        return data

    def getGradeSummary(self) -> dict:
        
        data = {
            'Title' : self.title,
            'Total' : 0,
            'Average' : 0
        }
        
        total = 0
        number_of_scores = 0
        for key, value in self.grade.items():
            for subkey, subvalue in value.items():
                if subkey == 'Score':
                    total += int(subvalue)
                    number_of_scores += 1
        data['Total'] = total
        data['Average'] = total / number_of_scores
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


    action_id = models.CharField(max_length=255, blank=True, default='') # Used to track actions ( 'Posts' , 'Comments' , 'Replies' )

    def __str__(self):
        return f"{self.name} - {self.school_id} - {self.email_address} - {self.contact_number}"
    
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
            'role' : 'School Admin'
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
    position = models.CharField(max_length=255, blank=True, default='Teacher I',
        choices=(
            ('Teacher I', 'Teacher I'), 
            ('Teacher II', 'Teacher II'), 
            ('Teacher III', 'Teacher III'), 
            ('Master Teacher I', 'Master Teacher I'),
            ('Master Teacher II', 'Master Teacher II'),
            ('Master Teacher III', 'Master Teacher III'),
            ('Master Teacher IV', 'Master Teacher IV'),
            ))
    job_started = models.DateTimeField(blank=True, null=True)
    job_ended = models.DateTimeField(blank=True, null=True)
    
    grade_level = models.CharField(max_length=255, blank=True, default='',
            choices=(
                ('Junior High School', 'Junior High School'),
                ('Senior High School', 'Senior High School'),
            )
                                   )
    department = models.CharField(max_length=255, blank=True, default='',
            choices=(
                ('Science', 'Science'),
                ('Filipino', 'Filipino'),
                ('Mathematics', 'Mathematics'),
                ('English', 'English'),
            ))
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

    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        self.fullname = f"{self.first_name} {self.middle_name} {self.last_name}"
        super().save(*args, **kwargs)
    
    def get_information(self):
        return {
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
        }
    
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
        difference = self.job_started - now
        
        days = difference.days
        months = (self.job_started.year - now.year) * 12 + self.job_started.month - now.month
        years = self.job_started.year - now.year
        
        
        return {
            "days": days,
            "months": months,
            "years": years
        }
        

    def update_is_evaluted(self):
        part_1 = IPCRFForm.objects.filter(employee_id=self.employee_id, form_type='PART 1').first() 
        
        if not part_1.is_checked:
            return 
        
        number_of_attachment_evaluated = 0
        attachments = RPMSAttachment.objects.filter(employee_id=self.employee_id)
        for attachment in attachments: 
            if attachment.is_checked :
                number_of_attachment_evaluated += 1
        
        if number_of_attachment_evaluated != 5 :
            return
        
        self.is_evaluated = True
        self.save()
    
    
    def get_recent_ipcrf_score(self):
        # Get the most recent IPCRF form by the creation date
        recent_form = IPCRFForm.objects.filter(employee_id=self.employee_id, form_type='PART 1', is_expired=False).order_by('-created_at').first()
        if recent_form:
            # Assuming the form has a method to get the average score
            scores = recent_form.getEvaluatorPart1Scores()
            # Calculate the overall average from the scores
            total_score = 0
            count = 0
            for key, value in scores.items():
                total_score += value['Average']
                count += 1
            if count > 0:
                return total_score / count
        return 0  # Return None if no recent form is found


    
    
    
# 1. title and scores for KBA BREAKDOWN
# 2. rule based classifier for Promotion
# 3. date of submission and score Performance tru year
# 4. generated text SWOT from COTForm 
