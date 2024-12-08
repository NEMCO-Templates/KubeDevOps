from base.models import *

def notification(request):
    if request.user.is_authenticated:  
        user = request.user
        notifications = Notification.objects.filter(user=user).order_by('-created')
        return {'notifications':notifications}
    else:
        return {}
import datetime
def get_user_last_access(request):
    if request.user.is_authenticated:  
        user = request.user
        last_access = user.last_login.strftime("%H:%M:%S").split(":")[0]
        time_now = datetime.datetime.now().strftime("%H:%M:%S").split(":")[0]
        
        last_access_day = user.last_login.strftime("%d-%m-%Y")
        time_now_day = datetime.datetime.now().strftime("%d-%m-%Y")
        
        online_status = False
        
        if int(time_now) - int(int(last_access)+3) <= 1 and last_access_day == time_now_day:
            online_status = True
            
        return {'online_status':online_status}
    else:
        return {}
        
        