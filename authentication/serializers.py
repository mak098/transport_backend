from rest_framework import serializers
from .models import User,TemporaryUser


class PrivateUserSerializer (serializers.ModelSerializer):
    class Meta:
        model = User
        fields= ('username', 'email', 'first_name', 'last_name','auth_token')
class UserSerializer (serializers.ModelSerializer):
    class Meta:
        model = User
        fields= ('username', 'email', 'first_name', 'last_name')
class TemporaryUserSerializer (serializers.ModelSerializer):
    class Meta:
        model = TemporaryUser
        fields= ('phone_number', 'otp','record_at')