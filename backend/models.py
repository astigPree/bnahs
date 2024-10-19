from django.db import models 
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
        return cls.objects.create(email=email, verification_link=link_key)
    

class MainAdmin(models.Model):
    username = models.CharField(max_length=255, blank=True, default='')
    password = models.CharField(max_length=255, blank=True, default='')
    
#     # total school
#     # total teacher
#     # number of forms answered


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
    
    is_accepted = models.BooleanField(default=False) # Is the school accepted
    created_at = models.DateTimeField(auto_now_add=True)

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
            'password' : self.password,
            'confirm_password' : self.confirm_password,
            'school_logo' : ''
        }
        
        if self.school_logo:
            if self.school_logo.url:
                school['school_logo'] = self.school_logo.url
        
        
    

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
            'password' : self.password,
            'confirm_password' : self.confirm_password,
        }
    
    
    def update_educations(self, data):
        self.educations = data
        self.save()
    
    
            


class Post(models.Model):
    post_owner = models.CharField(max_length=255, blank=True, default='') # Name or ID of owner of post
    title = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    liked = models.JSONField(default=list, blank=True)
    """
        liked = [
            employee_id,
            employee_id,
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
    post_id = models.IntegerField(default=0) # ID of post where comment is posted
    comment_owner = models.CharField(max_length=255, blank=True, default='')
    
    replied_to = models.CharField(max_length=255, blank=True, default='') # Name or ID where comment is replied
    is_seen = models.BooleanField(default=False) # Check if comment has been seen 
    
    def __str__(self):
        return f"{self.comment_owner} - {self.post_id}"
    
    def get_comment(self):
        return {
            'content' : self.content,
            'created_at' : self.created_at,
            'post_id' : self.post_id,
            'comment_owner' : self.comment_owner
        }
    


class RatingSheetForm(models.Model):
    pass
    # is_answered = models.BooleanField(default=False)
    # is_pending = models.BooleanField(default=False)
    # purpose = models.CharField(max_length=255, blank=True, default='',
    #     choices=(
    #         ('Evaluation', 'Evaluation'), 
    #         ('Admission', 'Admission'), 
    #         ('Other', 'Other')
    #     )
    # )
    # for_who = models.CharField(max_length=255, blank=True, default='')



class IndividualPerformanceForm(models.Model):
    pass



class ResultBasedForm(models.Model):
    pass


# class IPCRFForm(models.Model):
#     school_id = models.CharField(max_length=255, blank=True, default='')
#     employee_id = models.CharField(max_length=255, blank=True, default='')
#     evaluator_id = models.CharField(max_length=255, blank=True, default='')
#     form_type = models.CharField(max_length=255, blank=True, default='',
#             choices=(
#               ('PART 1', 'PART 1'), # Teacher to Evaluator
#               ('PART 2', 'PART 2'), # For Teacher
#               ('PART 3', 'PART 3'), # For Teacher
#             ))
    
#     content_for_teacher = models.JSONField(default=dict, blank=True)
#     """
    
#     # PART 1 DATA
#     {
        
#         "1" : {
#             "Question" : "Applied knowledge of content within and across curriculum teaching areas (PPST 1.1.2)",
#             "QUALITY" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "5"
#             },
#             "EFFICIENCY" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "1"
#             },
#             "TIMELINES" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "0"
#             }
#         },
#         "2" : {
#             "Question" : "Applied knowledge of content within and across curriculum teaching areas (PPST 1.1.2)",
#             "QUALITY" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "0"
#             },
#             "EFFICIENCY" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "0"
#             },
#             "TIMELINES" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "0"
#             }
#         }
        
        
#     }
    
    
#     """
    
#     """
    
#         # PART 2
#         {
#             "1" : {
#                 "Title" : "SELF-MANAGEMENT",
#                 "1" : "Sets personal goals and direction, needs and development.",
#                 "2" : "Sets personal goals and direction, needs and development.",
#                 "3" : "Sets personal goals and direction, needs and development.",
#                 "4" : "Sets personal goals and direction, needs and development.",
#                 "5" : "Sets personal goals and direction, needs and development.",
#                 "Selected" : [
#                     "1" , "2", "3"
#                 ]
#             },
#             "2" : {
#                 "Title" : "Professionalism and Ethics",
#                 "1" : "Sets personal goals and direction, needs and development.",
#                 "2" : "Sets personal goals and direction, needs and development.",
#                 "3" : "Sets personal goals and direction, needs and development.",
#                 "4" : "Sets personal goals and direction, needs and development.",
#                 "5" : "Sets personal goals and direction, needs and development.",
#                 "Selected" : [
#                     "1" , "2", "3"
#                 ]
#             }
#         }
        
#     """
    
#     """
    
#         # PART 3
#         {
#             "A" : {
#                 "Strenghts" : {
#                     "1" : {
#                         "QUALITY" : "2",
#                         "EFFICIENCY" : "5",
#                         "TIMELINES" : ""
#                     },
#                     "2" : {
#                         "QUALITY" : "2",
#                         "EFFICIENCY" : "",
#                         "TIMELINES" : ""
#                     },
#                 },
#                 "Development Needs" : {
#                     "1" : {
#                         "QUALITY" : "2",
#                         "EFFICIENCY" : "5",
#                         "TIMELINES" : ""
#                     },
#                     "2" : {
#                         "QUALITY" : "2",
#                         "EFFICIENCY" : "",
#                         "TIMELINES" : ""
#                     },
#                 },
#                 "Learning Objectives": {
#                     "1" : "Learning Objectives Learning Objectives Learning Objectives.",
#                     "2" : "Learning Objectives Learning Objectives Learning Objectives.",
#                 },
#                 "Intervention": {
#                     "1" : "Learning Objectives Learning Objectives Learning Objectives.",
#                     "2" : "Learning Objectives Learning Objectives Learning Objectives.",
#                 },
#                 "Timeline": {
#                     "1" : "Learning Objectives Learning Objectives Learning Objectives.",
#                     "2" : "Learning Objectives Learning Objectives Learning Objectives.",
#                 },
#                 "Resources Needs": {
#                     "1" : "Learning Objectives Learning Objectives Learning Objectives.",
#                     "2" : "Learning Objectives Learning Objectives Learning Objectives.",
#                 },
                
#             },
            
#             "B" : {
#                 "Selections" : {
#                     "1" : {
#                         "Title" : "SELF-MANAGEMENT",
#                         "Selected" : [
#                             "1" , "2", "3"
#                         ]
#                     },
#                     "2" : {
#                         "Title" : "Professionalism and Ethics",
#                         "Selected" : []
#                     },
#                 },
#                 "Learning Objectives": {
#                     "1" : "Learning Objectives Learning Objectives Learning Objectives.",
#                     "2" : "Learning Objectives Learning Objectives Learning Objectives.",
#                 },
#                 "Intervention": {
#                     "1" : "Learning Objectives Learning Objectives Learning Objectives.",
#                     "2" : "Learning Objectives Learning Objectives Learning Objectives.",
#                 },
#                 "Timeline": {
#                     "1" : "Learning Objectives Learning Objectives Learning Objectives.",
#                     "2" : "Learning Objectives Learning Objectives Learning Objectives.",
#                 },
#                 "Resources Needs": {
#                     "1" : "Learning Objectives Learning Objectives Learning Objectives.",
#                     "2" : "Learning Objectives Learning Objectives Learning Objectives.",
#                 },
#             }
            
#         }
        
    
#     """
    
#     content_for_evaluator = models.JSONField(default=dict, blank=True)
#     """
    
#     # PART 1 DATA
#     {
        
#         "1" : {
#             "Question" : "Applied knowledge of content within and across curriculum teaching areas (PPST 1.1.2)",
#             "QUALITY" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "0"
#             },
#             "EFFICIENCY" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "0"
#             },
#             "TIMELINES" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "0"
#             }
#         },
#         "2" : {
#             "Question" : "Applied knowledge of content within and across curriculum teaching areas (PPST 1.1.2)",
#             "QUALITY" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "0"
#             },
#             "EFFICIENCY" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "0"
#             },
#             "TIMELINES" : {
#                 "1" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "2" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "3" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "4" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "5" : "Demonstrated Level 3 in Objective 1 as shown in COT rating sheets / inter-observer agreement forms or No acceptable evidence was shown",
#                 "Rate" : "0"
#             }
#         }
        
        
#     }
    
    
#     """

#     created_at = models.DateTimeField(auto_now_add=True)

# class COTForm(models.Model):
#     school_id = models.CharField(max_length=255, blank=True, default='')
#     employee_id = models.CharField(max_length=255, blank=True, default='')
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     content = models.JSONField(default=dict, blank=True)
#     """
#         {
#             "Observer" : "Evaluator Name",
#             "Teacher Observed" : "Evaluated Name",
#             "Subject" : "Subject",
#             "Grade Level" : "Grade 7",
#             "Date : "September 05, 2023", !Save date after submiting,
#             "Questions" : {
#                 "1" : {
#                     "Objective" : "Applied knowledge of content within and across curriculum teaching areas. *",
#                     "Selected" : "7" !Selected rate
#                 },
#                 "2" : {
#                     "Objective" : "Applied knowledge of content within and across curriculum teaching areas. *",
#                     "Selected" : "7" !Selected rate, kung "NO" means its "3"
#                 }
#             },
#             "Comments" : ""
            
#         }
    
    
#     """
    


# class RPMSFolder(models.Model):
#     school_id = models.CharField(max_length=255, blank=True, default='')
#     employee_id = models.CharField(max_length=255, blank=True, default='')
#     created_at = models.DateTimeField(auto_now_add=True)
#     rpms_folder_id = models.CharField(max_length=255, blank=True, default='')
    

# class RPMSAClassWork(models.Model):
#     school_id = models.CharField(max_length=255, blank=True, default='')
#     employee_id = models.CharField(max_length=255, blank=True, default='')
#     created_at = models.DateTimeField(auto_now_add=True)
#     rpms_folder_id = models.CharField(max_length=255, blank=True, default='')
#     class_work_id = models.CharField(max_length=255, blank=True, default='') # id of the class work
#     title = models.CharField(max_length=255, blank=True, default='')
#     objectives = models.TextField(blank=True, default='')
#     """
#         {
#             "Instructions" : "<p>Hello World</p>"
#             "Objectives" : {
#                 "1" : {
#                     "Content" : "Established safe and secure learning environments to enhance learning through the consistent implementation of policies",
#                     "Score" : "5"
#                 }
#             },
#             "Comment" : " "
#         }
#     """


# class RPMSAttachment(models.Model):
#     school_id = models.CharField(max_length=255, blank=True, default='')
#     employee_id = models.CharField(max_length=255, blank=True, default='')
#     created_at = models.DateTimeField(auto_now_add=True)
    
    
#     streams_type = models.CharField(max_length=255, blank=True, default='')
#     """
#         "streams_type" : [
#             "KRA 1: Content Knowledge and Pedagogy", !Title ng RPMSContainer,
#             "KRA 3: Curriculum and Planning",  !Title ng RPMSContainer,
#         ]
#     """
#     file = models.FileField(upload_to='rpms_attachments')



# # 1. title and scores for KBA BREAKDOWN
# # 2. rule based classifier for Promotion
# # 3. date of submission and score Performance tru year
# # 4. generated text SWOT from COTForm 
