from django.db import models
import random
import string

# Create your models here.

def token_id_generator():
    
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
    
    while RedirectHandler.objects.filter(token=code).exists():
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=15))
    
    return code
    

class RedirectHandler(models.Model):
    user = models.CharField(max_length=255, blank=True, default='')
    token = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    redirect_url = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return f"{self.token} - {self.redirect_url}"
    
    @classmethod
    def create_token(cls , user : str , redirect_url : str):
        """
        This function is used to create token.
        
        """
        try:
            code = token_id_generator()
            handler = cls.objects.create(token=code, user=user, redirect_url=redirect_url.format(token=code))
            return handler
        
        except Exception as e:
            return None
        
        


# class HeadAdmin(models.Model):
#     username = models.CharField(max_length=255, blank=True, default='')
#     password = models.CharField(max_length=255, blank=True, default='')
    
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

    def __str__(self):
        return f"{self.name} - {self.school_id} - {self.email_address} - {self.contact_number}"
    

class People(models.Model):
    role = models.CharField(max_length=255, choices=(
        ('Evaluator', 'Evaluator'), 
        ('Teacher', 'Teacher')) , 
    blank=True, default='') # What the person does
    school_id = models.CharField(max_length=255, blank=True, default='') # Where the person belongs
    
    # ratings = models.IntegerField(default=0)
    # recomendation
    # work_start = models.DateTimeField(blank=True, null=True)
    # work_end = models.DateTimeField(blank=True, null=True)
    
    employee_id = models.CharField(max_length=255, blank=True, default='')
    first_name = models.CharField(max_length=255, blank=True, default='')
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



