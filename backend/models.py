from django.db import models

# Create your models here.


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
    blank=True, default='')
    
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
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Forms(models.Model):
    is_answered = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    purpose = models.CharField(max_length=255, blank=True, default='',
        choices=(
            ('Evaluation', 'Evaluation'), 
            ('Admission', 'Admission'), 
            ('Other', 'Other')
        )
    )
    for_who = models.CharField(max_length=255, blank=True, default='')



class Post(models.Model):
    post_owner = models.CharField(max_length=255, blank=True, default='') # Name of owner of post
    title = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    liked = models.JSONField(default=list)
    """
        liked = [
            employee_id,
            employee_id,
        ]
    """
    

class Comment(models.Model):
    content = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    post_id = models.IntegerField(default=0)
    comment_owner = models.CharField(max_length=255, blank=True, default='')
    

