from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'fullname','birth_date', 'gender', 'birth_country', 'current_country')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'fullname', 'birth_date', 'gender', 'birth_country', 'current_country')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            fullname = validated_data.get('fullname'),
            username=validated_data.get('username'),
            email=validated_data.get('email'),
            birth_date=validated_data.get('birth_date'),
            gender=validated_data.get('gender'),
            birth_country=validated_data.get('birth_country'),
            current_country=validated_data.get('current_country')
        )
        user.set_password(validated_data.get('password'))
        user.save()

        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = authenticate(username=username, password=password)
        
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        
        attrs['user'] = user
        return attrs
    

class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    
    
    
class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'fullname', 'birth_date', 'gender', 'birth_country', 'current_country']
        
    def validate(self, data):
        if not data:
            raise serializers.ValidationError("No data provided")
        return data
        
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True,validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, data):  
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data