from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(User)
admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(Message)
admin.site.register(Follower)
admin.site.register(Following)
admin.site.register(Notification)
admin.site.register(Games)
admin.site.register(Question)
admin.site.register(Score)