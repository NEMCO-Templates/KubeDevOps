from rest_framework.serializers import ModelSerializer
from base.models import *

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        
class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'

class RoomSerializer(ModelSerializer):
    topic = TopicSerializer(read_only=True)
    host = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Room
        fields = '__all__'
