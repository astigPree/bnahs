from django.db import models  



class Notifications(models.Model):
    action_id = models.CharField(max_length=255, blank=True, default='')
    action = models.CharField(max_length=255, blank=True, default='')
    name = models.CharField(max_length=255, blank=True, default='')
    content = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True) 
    post_id = models.CharField(max_length=255, blank=True, default='')
    comment_id = models.CharField(max_length=255, blank=True, default='')
    notification_type = models.CharField(max_length=255, blank=True, default='') 
    """
        notification_type = "POST"
    """

    def __str__(self):
        return f"{self.action} - {self.name} - {self.content}"
    
    def get_notification_by_array(self):
        return [
            self.action_id,
            self.content,
            self.name
        ]

    def get_notification(self):
        return {
            'action_id' : self.action_id,
            'action' : self.action,
            'name' : self.name,
            'content' : self.content,
            'created_at' : self.created_at,
            'notification_type' : self.notification_type,
            'post_id' : self.post_id
        }

class Post(models.Model):
    post_owner = models.CharField(max_length=255, blank=True, default='') # Action ID of owner of post
    content = models.TextField(blank=True, default='') # Content of post
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    post_id = models.CharField(max_length=255, blank=True, default='') # Generated id by system to identify post
    liked : list = models.JSONField(default=list, blank=True)
    """
        liked = [
            action_id,
            action_id,
        ]
    """
    
    commented : list = models.JSONField(default=list, blank=True)
    """
        commented = [
            action_id,
            action_id,
        ]
    """
    
    mentions : list = models.JSONField(default=list, blank=True)
    """
        mentions = [
            [action_id, name],
            [action_id, name],
        ]
    """
    
    notifications : list = models.JSONField(default=list, blank=True)
    """
        notifications = [
            [action_id, action, name],
            [action_id, action, name],
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
            'created_at' : self.created_at,
            'post_id' : self.post_id,
            'mentions' : self.mentions,
            'notifications' : [],
            'number_of_comments' : 0
        }
        
        notifications = Notifications.objects.filter(post_id=self.post_id , notification_type = "POST").order_by('-created_at')
        for notification in notifications:
            data['notifications'].append(notification.get_notification_by_array())

        number_of_comments = Comment.objects.filter(post_id=self.post_id).count()
        data['number_of_comments'] = number_of_comments
        
        if self.liked:
            data['number_of_likes'] = len(self.liked)
        
        if action_id:
            if action_id in self.liked:
                data['liked'] = True
            if action_id in self.commented:
                data['commented'] = True
        
        return data
               
               
    def add_notification(self, action_id, action, name):
        content_len = 20
        if action == "liked":
            content = f"{name} liked your post : {self.content[:content_len] if len(self.content) > content_len else self.content}..."
            # self.notifications.insert( 0, [action_id, action, name])
            notification = Notifications.objects.create(
                action_id=action_id, action=action, 
                name=name, content=content, 
                post_id=self.post_id,
                notification_type = "POST"
            )
            
        elif action == "commented":
            content = f"{name} commented on your post : {self.content[:content_len] if len(self.content) > content_len else self.content}..."
            # self.notifications.insert( 0, [action_id, action, name])
            notification = Notifications.objects.create(
                action_id=action_id, action=action, 
                name=name, content=content, 
                post_id=self.post_id
            )
        elif action == "mentioned":
            content = f"{name} mentioned you in your post : {self.content[:content_len] if len(self.content) > content_len else self.content}..."
            # self.notifications.insert( 0, [action_id, action, name])  
            notification = Notifications.objects.create(
                action_id=action_id, action=action, 
                name=name, content=content, 
                post_id=self.post_id,
                notification_type = "POST"
            )      
        elif action == "replied":
            content = f"{name} replied to your comment : {self.content[:content_len] if len(self.content) > content_len else self.content}..."
            # self.notifications.insert( 0, [action_id, action, name])
            notification = Notifications.objects.create(
                action_id=action_id, action=action, 
                name=name, content=content, 
                post_id=self.post_id,
                notification_type = "POST"
            )
        elif action == "posted":
            content = f"{name} posted a new post : {self.content[:content_len] if len(self.content) > content_len else self.content}..."
            # self.notifications.insert( 0, [action_id, action, name])
            notification = Notifications.objects.create(
                action_id=action_id, action=action, 
                name=name, content=content, 
                post_id=self.post_id,
                notification_type = "POST"
            ) 
    
    def add_commented(self, action_id):
        self.commented.append(action_id)
        self.save()
        
    def add_mentions(self, action_id, name):
        self.mentions.append([action_id, name])
        self.save()

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

    comment_id = models.CharField(max_length=255, blank=True, default='') # Generated id by system to identify comment
    post_id = models.CharField(max_length=255, blank=True, default='') # post_id of post where comment is posted
    comment_owner = models.CharField(max_length=255, blank=True, default='') # Action ID of owner of comment

    is_private = models.BooleanField(default=False) # Used to identify if it private
    replied_to = models.CharField(max_length=255, blank=True, default='') # Action ID where comment is replied
    is_seen = models.JSONField(default=list, blank=True)
    """
        is_seen = [
            action_id,
            action_id,
        ]
    """ 
    
    commented : list = models.JSONField(default=list, blank=True)
    """
        commented = [
            action_id,
            action_id,
        ]
    """
    
    liked : list = models.JSONField(default=list, blank=True)
    """
        liked = [
            action_id,
            action_id,
        ]
    """
    
        
    mentions : list = models.JSONField(default=list, blank=True)
    """
        mentions = [
            [action_id, name],
            [action_id, name],
        ]
    """
    
    notifications : list = models.JSONField(default=list, blank=True)
    """
        notifications = [
            [action_id, action, name],
            [action_id, action, name],
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
            'created_at' : self.created_at,
            'is_private' : self.is_private,
            'comment_id' : self.comment_id, 
            'mentions' : self.mentions,
            'notifications' : []
        }
        
        notifications = Notifications.objects.filter(post_id=self.comment_id , notification_type = "POST").order_by('-created_at')
        for notification in notifications:
            data['notifications'].append(notification.get_notification_by_array())
        
        if action_id:
            if action_id in self.is_seen:
                data['is_seen'] = True 
        
        data['number_of_likes'] = len(self.liked)
        
        if action_id:
            if action_id in self.liked:
                data['liked'] = True
            if action_id in self.commented:
                data['commented'] = True
        
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
 
 
    def add_notification(self, action_id, action, name):
        content_len = 20
        if action == "liked":
            content = f"{name} liked your comment : {self.content[:content_len] if len(self.content) > content_len else self.content}..."
            # self.notifications.insert( 0, [action_id, action, name])
            Notifications.objects.create(
                action_id=action_id, action=action, 
                name=name, content=content, 
                comment_id=self.comment_id,
                notification_type = "POST"
            )
        elif action == "commented":
            content = f"{name} commented on your post : {self.content[:content_len] if len(self.content) > content_len else self.content}..."
            # self.notifications.insert( 0, [action_id, action, name])
            Notifications.objects.create(
                action_id=action_id, action=action, 
                name=name, content=content, 
                comment_id=self.comment_id,
                notification_type = "POST"
            )
        elif action == "mentioned":
            content = f"{name} mentioned you in your post : {self.content[:content_len] if len(self.content) > content_len else self.content}..."
            # self.notifications.insert( 0, [action_id, action, name])
            Notifications.objects.create(
                action_id=action_id, action=action, 
                name=name, content=content, 
                comment_id=self.comment_id,
                notification_type = "POST"
            )
        elif action == "replied":
            content = f"{name} replied to your comment : {self.content[:content_len] if len(self.content) > content_len else self.content}..."
            # self.notifications.insert( 0, [action_id, action, name])
            Notifications.objects.create(
                action_id=action_id, action=action, 
                name=name, content=content, 
                comment_id=self.comment_id,
                notification_type = "POST"
            )
        elif action == "posted":
            content = f"{name} posted a new post : {self.content[:content_len] if len(self.content) > content_len else self.content}..."
            # self.notifications.insert( 0, [action_id, action, name])
            Notifications.objects.create(
                action_id=action_id, action=action, 
                name=name, content=content, 
                comment_id=self.comment_id,
                notification_type = "POST"
            )
        self.save()
    
 
 
 
 
 
 
 
class LastFormCreated(models.Model):
    school_year = models.CharField(max_length=255, blank=True, default='')    
    is_for_teacher_proficient = models.BooleanField(default=False) # If True, the folder is for teacher proffecient
    form_id = models.CharField(max_length=255, blank=True, default='') 
    form_type = models.CharField(max_length=255, blank=True, default='')
    
    """
        form_type = 'COT'
        form_type = 'IPCRF'
        form_type = 'RPMSFolder' 
        form_type = 'RPMSClassWork' 
        form_type = 'RPMSAttachment' 
    """
    school_id = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.form_type} - {self.school_year}"