from django.db import models 
from django.conf import settings
from django.utils import timezone

import uuid
# Create your models here.

def generate_link_key():
    link_key = str(uuid.uuid4())
    while VerificationLink.objects.filter(verification_link=link_key).exists():
        link_key = str(uuid.uuid4())
    return link_key

class VerificationLink(models.Model):
    email = models.CharField(max_length=255, blank=True, default='')
    verification_link = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    
    @classmethod
    def generate_link(cls, email):
        link_key = generate_link_key()
        cls.objects.create(email=email, verification_link=link_key)
        
        return f"{settings.MY_HOST}register/school/verifications/{link_key}"
    
    def is_expired(self, expire_in_minutes=30):
        return self.created_at < (timezone.now() - timezone.timedelta(minutes=expire_in_minutes))

    

class MainAdmin(models.Model):
    username = models.CharField(max_length=255, blank=True, default='')
    password = models.CharField(max_length=255, blank=True, default='')
    
    
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
            'is_accepted' : self.is_accepted
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
    position = models.CharField(max_length=255, blank=True, default='',
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
    
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

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
        }
    
    
    def update_educations(self, data):
        self.educations = data
        self.save()
    


class Post(models.Model):
    post_owner = models.CharField(max_length=255, blank=True, default='') # Action ID of owner of post
    title = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField(blank=True, default='') # Content of post
    content_file = models.FileField(upload_to='uploads/', default='', blank=True, null=True) # File uploaded by user
    created_at = models.DateTimeField(auto_now_add=True)
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
    
    def __str__(self):
        return f"{self.post_owner} - {self.title}"
    
    
    def get_post(self):
        return {
            'post_owner' : self.post_owner,
            'title' : self.title,
            'content' : self.content,
            'created_at' : self.created_at,
            'liked' : self.liked
        }
    

class Comment(models.Model):
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    post_id = models.IntegerField(default=0) # post_id of post where comment is posted
    comment_owner = models.CharField(max_length=255, blank=True, default='') # Action ID of owner of comment
    attachment = models.FileField(upload_to='comment/', blank=True, default='')
    
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
    
    def get_comment(self):
        data = {
            'content' : self.content,
            'created_at' : self.created_at,
            'post_id' : self.post_id,
            'comment_owner' : self.comment_owner,
            'replied_to' : self.replied_to,
            'is_seen' : self.is_seen,
            'attachment' : '',
        }
        
        if self.attachment or self.attachment != "":
            data['attachment'] = self.attachment.url
            
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
        
        "1" : {
            "Question" : "Applied knowledge of content within and across curriculum teaching areas (PPST 1.1.2)",
            "QUALITY" : {
                "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "Rate" : "5"
            },
            "EFFICIENCY" : {
                "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
                "Rate" : "1"
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
                "Selected" : [
                    "1" , "2", "3"
                ]
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
                "Strenghts" : {
                    "1" : {
                        "QUALITY" : "2",
                        "EFFICIENCY" : "5",
                        "TIMELINES" : ""
                    },
                    "2" : {
                        "QUALITY" : "2",
                        "EFFICIENCY" : "",
                        "TIMELINES" : ""
                    },
                },
                "Development Needs" : {
                    "1" : {
                        "QUALITY" : "2",
                        "EFFICIENCY" : "5",
                        "TIMELINES" : ""
                    },
                    "2" : {
                        "QUALITY" : "2",
                        "EFFICIENCY" : "",
                        "TIMELINES" : ""
                    },
                },
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
                "Selections" : {
                    "1" : {
                        "Title" : "SELF-MANAGEMENT",
                        "Selected" : [
                            "1" , "2", "3"
                        ]
                    },
                    "2" : {
                        "Title" : "Professionalism and Ethics",
                        "Selected" : []
                    },
                },
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
    created_at = models.DateTimeField(auto_now_add=True)
    
    
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
            'content_for_evaluator' : self.content_for_evaluator
        }
        
        # Find the evaluator
        if self.evaluator_id or self.evaluator_id != '':
            evaluator = People.objects.filter(school_id=self.school_id, employee_id=self.evaluator_id).first()
            if evaluator:
                data['evaluator'] = evaluator.get_information()
        
        if self.form_type == 'PART 1':
            """
            {
                "1" : {
                    "QUALITY" : "0",
                    "EFFICIENCY" : "0",
                    "TIMELINES" : "0",
                    "Total" : "0"
                },
                "2" : {
                    "QUALITY" : "0",
                    "EFFICIENCY" : "0",
                    "TIMELINES" : "0",
                    "Total" : "0"
                },
            }
            """
            try : 
                for key in self.content_for_teacher:
                    data[key] = {}
                    total = 0
                    if 'QUALITY' in self.content_for_teacher[key]:
                        quality_rate = self.content_for_teacher[key]['QUALITY']['Rate']
                        data[key]['QUALITY'] = quality_rate
                        total += int(quality_rate)
                    if 'EFFICIENCY' in self.content_for_teacher[key]:
                        efficiency_rate = self.content_for_teacher[key]['EFFICIENCY']['Rate']
                        data[key]['EFFICIENCY'] = self.content_for_teacher[key]['EFFICIENCY']['Rate']
                        total += int(efficiency_rate)
                    if 'TIMELINES' in self.content_for_teacher[key]:
                        timelines_rate = self.content_for_teacher[key]['TIMELINES']['Rate']
                        data[key]['TIMELINES'] = self.content_for_teacher[key]['TIMELINES']['Rate']
                        total += int(timelines_rate)
                    data[key]['Total'] = total
            except Exception as e :
                data['Error'] = str(e)
        
        if self.form_type == 'PART 2':
            pass
            # TODO : Add content for part 2

        
        if self.form_type == 'PART 3':
            pass
            # TODO : Add content for part 3
        
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
                rates = [] # List of rates
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
                data[key]['Average'] = total / len(rates)
        
        
        return data
    
    def getEvaluatorPart1Scores(self):
        data = {}
        content_for_evaluator = self.content_for_evaluator
        if content_for_evaluator:
            for key in content_for_evaluator:
                data[key] = {}
                total = 0
                if 'QUALITY' in self.content_for_evaluator[key]:
                    quality_rate = self.content_for_evaluator[key]['QUALITY']['Rate']
                    data[key]['QUALITY'] = quality_rate
                    total += int(quality_rate)
                if 'EFFICIENCY' in self.content_for_evaluator[key]:
                    efficiency_rate = self.content_for_evaluator[key]['EFFICIENCY']['Rate']
                    data[key]['EFFICIENCY'] = self.content_for_evaluator[key]['EFFICIENCY']['Rate']
                    total += int(efficiency_rate)
                if 'TIMELINES' in self.content_for_evaluator[key]:
                    timelines_rate = self.content_for_evaluator[key]['TIMELINES']['Rate']
                    data[key]['TIMELINES'] = self.content_for_evaluator[key]['TIMELINES']['Rate']
                    total += int(timelines_rate)
                data[key]['Total'] = total
                
        return data
    
    
    
class COTForm(models.Model):
    """
        Form for evaluator to evaluate a teacher
    """
    school_id = models.CharField(max_length=255, blank=True, default='')
    employee_id = models.CharField(max_length=255, blank=True, default='') # ID of evaluator
    evaluated_id = models.CharField(max_length=255, blank=True, default='') # ID of teacher
    created_at = models.DateTimeField(auto_now_add=True)
    
    status = models.CharField(max_length=255, blank=True, default='Pending',
        choices=(
         ('Pending', 'Pending'),
         ('Approved', 'Approved'),
         ('Rejected', 'Rejected'),
         ('Cancelled', 'Cancelled'),
         ('Completed', 'Completed'),
        ))
    
    content = models.JSONField(default=dict, blank=True)
    """
        {
            "Observer" : "Evaluator Name",
            "Teacher Observed" : "Evaluated Name",
            "Subject" : "Subject",
            "Grade Level" : "Grade 7",
            "Date : "September 05, 2023", !Save date after submiting,
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
    

    def __str__(self):
        return f"{self.school_id} - {self.employee_id} - {self.created_at}"
    
   
    def get_information(self):
        data =  {
            'form' : 'COTForm',
            'school_id' : self.school_id,
            'employee_id' : self.employee_id,
            'created_at' : self.created_at,
            'content' : self.content,
            'status' : self.status
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
        Based on the following evaluation data, what are the strengths?
        Objectives and Ratings:
        """

        weaknesses_prompt = """
        Based on the following evaluation data, what are the weaknesses?
        Objectives and Ratings:
        """

        opportunities_prompt = """
        Based on the following evaluation data, what are the opportunities?
        Objectives and Ratings:
        """

        threats_prompt = """
        Based on the following evaluation data, what are the threats?
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
    school_id = models.CharField(max_length=255, blank=True, default='')
    employee_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    rpms_folder_id = models.CharField(max_length=255, blank=True, default='')
    
    
    def __str__(self):
        return f"{self.school_id} - {self.employee_id} - {self.created_at}"
    

class RPMSClassWork(models.Model):
    """_summary_

        A class to represent a classwork created by Head Adminstrator. 
        This where the RPMS Attachement is uploaded.
    
 
    """
    
    
    school_id = models.CharField(max_length=255, blank=True, default='')
    employee_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    rpms_folder_id = models.CharField(max_length=255, blank=True, default='')
    class_work_id = models.CharField(max_length=255, blank=True, default='') # id of the class work
    title = models.CharField(max_length=255, blank=True, default='')
    objectives = models.JSONField(default=dict, blank=True)
    """
        {
            "Instructions" : "<p>Hello World</p>"
            "Objectives" : {
                "1" : {
                    "Content" : "Established safe and secure learning environments to enhance learning through the consistent implementation of policies",
                    "Score" : "5"
                }
            },
            "Comment" : " "
        }
    """


class RPMSAttachment(models.Model):
    """
        A class to represent a attachment in the RPMS Classwork.
        This is uploaded to the RPMS Classwork.
    
    """
    
    
    school_id = models.CharField(max_length=255, blank=True, default='')
    employee_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
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
    streams_type = models.CharField(max_length=255, blank=True, default='')
    """
        "streams_type" : [
            "KRA 1: Content Knowledge and Pedagogy", !Title ng RPMSContainer,
            "KRA 3: Curriculum and Planning",  !Title ng RPMSContainer,
        ]
    """
    
    file = models.FileField(upload_to='rpms_attachments')
    grade = models.JSONField(default=dict, blank=True)
    """
        {
            "1" : {
                "Content" : "KRA 1: Content Knowledge and Pedagogy",
                "Score" : "5"
            },
            "2" : {
                "Content" : "KRA 1: Content Knowledge and Pedagogy",
                "Score" : "5"
            }
        }
    
    """
    
    def __str__(self):
        return f"{self.school_id} - {self.employee_id} - {self.created_at}"
    
    def get_information(self):
        data =  {
            'form' : 'RPMSAttachment',
            'school_id' : self.school_id,
            'employee_id' : self.employee_id,
            'created_at' : self.created_at,
            'class_work_id' : self.class_work_id,
            'status' : self.status
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
        
        return data

    def getTotalScores(self):
        total = 0
        for key, value in self.grade.items():
            for subkey, subvalue in value.items():
                if subkey == 'Score':
                    total += int(subvalue)
        return total

# 1. title and scores for KBA BREAKDOWN
# 2. rule based classifier for Promotion
# 3. date of submission and score Performance tru year
# 4. generated text SWOT from COTForm 
