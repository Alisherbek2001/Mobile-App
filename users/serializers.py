from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name','birth_date', 'gender', 'birth_country', 'current_country')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'birth_date', 'gender', 'birth_country', 'current_country')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            first_name = validated_data.get('first_name'),
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
    