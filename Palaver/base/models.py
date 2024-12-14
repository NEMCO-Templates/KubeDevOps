from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
# Create your models here.


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique= True, null=True)
    bio = models.TextField(null=True)
    avatar = models.ImageField(null=True, default='avatar.svg')
    followers = models.ManyToManyField('self', related_name='followingUsersModel', symmetrical=False, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    
    def get_user_last_access(self):
        last_access = self.last_login.strftime("%H:%M:%S").split(":")[0]
        time_now = datetime.now().strftime("%H:%M:%S").split(":")[0]
        
        last_access_day = self.last_login.strftime("%d-%m-%Y")
        time_now_day = datetime.now().strftime("%d-%m-%Y")

        online_status = False
        
        if int(time_now) - int(int(last_access)+3) <= 1 and last_access_day == time_now_day:
            online_status = True
        
        return online_status

class Follower(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name='followersUsers', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'follower')

    def __str__(self):
        return f'{self.follower.email} follows {self.user.email}'

    @classmethod
    def get_followers_count(cls, user):
        return cls.objects.filter(user=user).count()

class Following(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='followingUsers', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'following')

    def __str__(self):
        return f'{self.user.email} follows {self.following.email}'

    @classmethod
    def get_following_count(cls, user):
        return cls.objects.filter(user=user).count()
    
    
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    notificationType = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=200, default="#")
    fromUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fromUser', default=None, null=True)
    
    def __str__(self):
        return self.title
    
    def get_notification_count(user):
        return Notification.objects.filter(user=user).count()
    


class Topic(models.Model):
    name = models.CharField(max_length=200)
    
    
    def __str__(self):
        return self.name



#######################################################################################
class Room(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    up_votes = models.ManyToManyField(User, related_name='up_votes', blank=True)
    down_votes = models.ManyToManyField(User, related_name='down_votes', blank=True)
    
    
    class Meta:
        ordering = ['-updated', '-created']
    
    def __str__(self):
        return self.name
    
    def get_up_votes(self):
        return self.up_votes.count()
    
    def get_down_votes(self):
        return self.down_votes.count()
#######################################################################################
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=200, null=True)
    user_avatar = models.ImageField(null=True, default='avatar.svg')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(default=datetime.now, blank=True)
    
    def __str__(self):
        return self.body[0:50]
    
    class Meta:
        ordering = ['-updated', '-created']
        
        
        
class Games(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    
class Question(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    question_text = models.TextField()
    question_type = models.CharField(max_length=200, default="text")
    correct_answer = models.CharField(max_length=200)
    question_image = models.ImageField(null=True, blank=True)
    completed_by = models.ManyToManyField(User, blank=True)
    
    def __str__(self):
        return self.question_text
    
    
class Score(models.Model):
    game = models.ForeignKey(Games, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s score for {self.game.name}"