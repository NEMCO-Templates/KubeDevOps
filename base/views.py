from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from .models import *
from .forms import RoomForm, UserForm, MyUserCreationForm
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse

# rooms = [
#     {'id':1, 'name':'Lets learn python!'},
#     {'id':2, 'name':'Design with me'},
#     {'id':3, 'name':'Front-end developers'},
# ]


def metrics(request):
    metrics_data = generate_latest()
    return HttpResponse(metrics_data, content_type=CONTENT_TYPE_LATEST)

def loginPage(request):
    
    page = "login"
    
    if request.user.is_authenticated:
        messages.success(request, "You are already logged in")
        return redirect('home')
    
    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email) 
        except:
            messages.error(request, "Username does not exist")
            return redirect('login')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully")
            return redirect('home')
        else:
            messages.error(request, "Username or password is incorrect")
            return redirect('login')
    
    context = {"page":page}
    return render(request, 'base/login_register.html', context)



def logoutUser(request):
    logout(request)
    messages.success(request, "Logged out successfully")
    return redirect('home')


def registerPage(request):
    page = "register"
    
    form = MyUserCreationForm()
    
    if request.method == "POST":
        form = MyUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error has occurred during registration")
    
    
    context = {"page":page, "form":form, 'is_register_page': True}
    return render(request, 'base/login_register.html', context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains = q) | 
        Q(description__icontains = q)
        )
    topics = Topic.objects.all()
    room_count = rooms.count()
    
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q) | 
        Q(room__name__icontains=q)
        )
    
    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    
    return render(request, 'base/home.html', context)


def room(request, pk):
    username = request.user.username
    room = Room.objects.get(id=pk)
    # room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
 
    context = {'username': username, 'room': room, 'participants':participants}
    
    return render(request, 'base/room.html', context)

def send(request):
    body = request.POST['body']
    room_id = request.POST['room_id']
    
    room_details = Room.objects.get(id=room_id)
    
    new_message = Message.objects.create(body=body, user=request.user, room=room_details, username = request.user.username, user_avatar = request.user.avatar.url)
    room_details.participants.add(request.user)
    new_message.save()
    return HttpResponse('Message sent successfully')

@api_view(['GET'])
def getMessages(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('-created')
    serializers = MessageSerializer(room_messages, many=True).data
    return Response(serializers)

# def room(request, pk):
#     room = Room.objects.get(id=pk)
#     room_messages = room.message_set.all().order_by('-created')
#     participants = room.participants.all()
#     if request.method == "POST": 
#         body = request.POST.get('body')
#         message = Message.objects.create(body=body, user=request.user, room=room)
#         room.participants.add(request.user)
#         return redirect('room', pk=room.id)
    
    
#     context = {'room': room, 'room_messages':room_messages, 'participants':participants}
    
#     return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    
    followers = user.followingUsers.all()
    following = user.followersUsers.all()
    
    followers_count = Follower.get_followers_count(user)
    following_count = Following.get_following_count(user)
    
    
    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages, 'topics':topics, 'followers_count':followers_count, 'following_count':following_count, 'followers':followers, 'following':following}
    return render(request, 'base/profile.html', context)



def follow_user(request, userId):
    user = request.user
    following = User.objects.get(id=userId)
    if not Follower.objects.filter(user=following, follower=user).exists():
        user.followers.add(following)
        Follower.objects.create(user=following, follower=user)
        Following.objects.create(user=user, following=following)
        notification = Notification.objects.create(title=f"{user.username} started following you", link=f"/profile/{user.id}", user=following, notificationType="follow", fromUser=user)
        messages.success(request, f'You are now following {following.username}!')
    else:
        messages.warning(request, f'You are already following {following.username}!')
    return redirect('user-profile', pk=userId)


def unfollow_user(request, userId):
    user = request.user
    following = User.objects.get(id=userId)
    if Follower.objects.filter(user=following, follower=user).exists():
        user.followers.remove(following)
        Follower.objects.filter(user=following, follower=user).delete()
        Following.objects.filter(user=user, following=following).delete()
        messages.success(request, f'You are no longer following {following.username}!')
    else:
        messages.warning(request, f'You are not following {following.username}!')
    return redirect('user-profile', pk=userId)

def delete_notification(request, pk):
    notification = Notification.objects.get(id=pk)
    notification.delete()
    return redirect(request.META['HTTP_REFERER'])
    
        

@login_required(login_url='login')
def createRoom(request):
    topics = Topic.objects.all()
    form = RoomForm()
    
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        
        return redirect('home')
    
    context = {'form':form, 'topics':topics}
    
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse("You are not allowed to do this")
    
    if request.method == "POST":
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        
        return redirect('home')
    
    
    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)
    
@login_required(login_url='login')  
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse("You are not allowed to do this")
    
    if request.method == "POST":
        room.delete()
        return redirect('home')
    
    context = {'obj':room}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')  
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    
    if request.user != message.user:
        return HttpResponse("You are not allowed to do this")
    
    if request.method == "POST":
        message.delete()
        return redirect('home')
    
    context = {'obj':message}
    return render(request, 'base/delete.html', context)
    
       
@login_required(login_url='login')
def updateUser(request):
    form = UserForm(instance=request.user)
    
    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=request.user.id)
        
    context = {'form':form}
    
    return render(request, 'base/update_user.html', context)
    

def topicsPage(request):
    t = request.GET.get('t') if request.GET.get('t') != None else ''
    
    topics = Topic.objects.filter(
        Q(name__icontains=t)
    )
    
    context = {'topics':topics}
    
    return render(request, 'base/topics.html', context)


def activityPage(request):
    activities = Message.objects.all()
    
    context = {'activities':activities}
    
    return render(request, 'base/activity.html', context)


def gamePage(request):
    games = Games.objects.all()
    context = {'games':games}
    return render(request, 'base/gameCenter.html', context)


def startGame(request, pk):
    game = Games.objects.get(id=pk)
    scoreUser, created = Score.objects.get_or_create(game=game, user=request.user)
    scores = Score.objects.filter(game=game).order_by('-score')
    context = {'game':game, 'scoreUser':scoreUser, 'scores':scores}
    return render(request, 'base/startGame.html', context)


def gameForm(request):
    return render(request, 'base/gameForm.html')


import random

def game_view(request, game_id):
    game = get_object_or_404(Games, pk=game_id)
    questions = Question.objects.filter(game=game).exclude(completed_by=request.user).all()
    
    correct = 0
    # print(question_sample)
    i = 1
    if request.method == 'POST':
        print(request.POST)
        for question in questions:
            answer = request.POST.get(f'answer_{question.id}', '')
            if answer == question.correct_answer:
                correct += 1
                question.completed_by.add(request.user)
        score = Score.objects.get(game=game, user=request.user)
        score.score = correct
        score.save()
        return redirect('game')
        
    context = {'game': game, 'questions': questions}
    return render(request, 'base/gameForm.html', context)


def game_leaderboard(request):
    leaderboard = Leaderboard.objects.all()
    context = {'leaderboard':leaderboard}
    return render(request, 'base/leaderboard.html', context)




#######################################################################################

@login_required(login_url='login')
def up_vote_room(request, pk):
    room = Room.objects.get(id=pk)
    
    if room.up_votes.filter(id=request.user.id).exists():
        room.up_votes.remove(request.user)
        messages.success(request, f'You have removed your up vote')

    elif room.down_votes.filter(id=request.user.id).exists() and room.up_votes.filter(id=request.user.id).exists() == False:
        room.down_votes.remove(request.user)
        room.up_votes.add(request.user)
        messages.success(request, f'You have up voted the room')

    else:
        room.up_votes.add(request.user)
        messages.success(request, f'You have up voted the room')
    

    return redirect('home')
#######################################################################################

#######################################################################################

@login_required(login_url='login')
def down_vote_room(request, pk):
    room = Room.objects.get(id=pk)
    
    if room.down_votes.filter(id=request.user.id).exists():
        room.down_votes.remove(request.user)
        messages.success(request, f'You have removed your down vote')

    elif room.up_votes.filter(id=request.user.id).exists() and room.down_votes.filter(id=request.user.id).exists() == False:
        room.up_votes.remove(request.user)
        room.down_votes.add(request.user)
        messages.success(request, f'You have down voted the room')

    else:
        room.down_votes.add(request.user)
        messages.success(request, f'You have down voted the room')
    

    return redirect('home')
#######################################################################################