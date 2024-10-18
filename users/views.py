import os
from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.contrib.auth import update_session_auth_hash
from drf_yasg.utils import swagger_auto_schema
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.urls import reverse

from .serializers import ForgotPasswordSerializer, RegisterSerializer, LoginSerializer,UsernameCheckSerializer,UserSerializer,ProfileUpdateSerializer,PasswordChangeSerializer
from .models import User


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        response_data = {
            'user': serializer.data,
            'refresh': str(refresh),
            'access': access,
        }
        return Response(response_data,status=status.HTTP_201_CREATED)
    
    
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class CheckUsernameView(APIView):
    @swagger_auto_schema(request_body=UsernameCheckSerializer)
    def post(self, request, *args, **kwargs):
        serializer = UsernameCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        user_exists = User.objects.filter(username=username).exists()
        if user_exists:
            return Response("This username already exist",status=status.HTTP_200_OK)  
        else:
            return Response("Username doesn't exist",status=status.HTTP_204_NO_CONTENT)
        
        
class ProfileUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(responses={200: ProfileUpdateSerializer})
    def get(self,request,*args,**kwargs):
        user = request.user
        serializer = ProfileUpdateSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(request_body=ProfileUpdateSerializer, responses={200: 'Profile update successfully'})
    def put(self,request,*args,**kwargs):
        user = request.user        
        serializer = ProfileUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'Profile update successfully'},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(responses={200: 'Account deleted successfully'})
    def delete(self,request,*args,**kwargs):
        user = request.user
        user.delete()
        return Response({'message':'Account deleted successfully.'}, status=status.HTTP_200_OK)
    

class PasswordChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(request_body=PasswordChangeSerializer,responses={200:'Password update successfully'})
    def put(self,request):
        serializer = PasswordChangeSerializer(data=request.data)
        user = request.user
        if serializer.is_valid():
            if not user.check_password(serializer.data.get("old_password")):
                return Response({"old_password":"Wrong password."},status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get('new_password'))
            user.save()
            update_session_auth_hash(request,user)
            return Response({"message":"Password changed successfully."},status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPIView(APIView):
    @swagger_auto_schema(request_body=ForgotPasswordSerializer,responses={200:'Email send succesfully'})
    def post(self, request):
        email = request.data.get('email').strip().lower()  # Strips spaces and converts to lowercase
        user = User.objects.filter(email=email).first()
        
        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token}))
            
            send_mail(
                'Password Reset Request',
                f'Use the following link to reset your password: {reset_url}',
                os.getenv('DEFAULT_FROM_EMAIL'),
                [user.email],
                fail_silently=False,
            )
            return Response({"message":"Password reset link sent to your email"})
        return Response({"error":"Email not found."},status=status.HTTP_404_NOT_FOUND)


class PasswordResetConfirmAPIView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        
        token_generator = PasswordResetTokenGenerator()
        if user and token_generator.check_token(user, token):
            return render(request, 'reset_password.html', {'uidb64': uidb64, 'token': token})
        else:
            return Response({"error": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)
        
    def post(self,request,uidb64, token):
        new_password = request.data.get('new_password')
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        token_generator = PasswordResetTokenGenerator()
        if user and token_generator.check_token(user, token):
            user.set_password(new_password)
            user.save()
            return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)


class AccountDeleteRequestAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        user = request.user
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        delete_url = request.build_absolute_uri(reverse('account-delete-confirm', kwargs={'uidb64': uid, 'token': token}))
        
        send_mail(
            'Account Deletion Request',
            f'Click the following link to delete your account: {delete_url}',
            os.getenv('DEFAULT_FROM_EMAIL'),
            [user.email],
            fail_silently=False,
        )
        return Response({"message": "Account deletion confirmation link sent to your email."}, status=status.HTTP_200_OK)
    

class AccountDeleteConfirmAPIView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()
        if user and token_generator.check_token(user, token):
            user.delete()
            return Response({"message": "Account deleted successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid token or user."}, status=status.HTTP_400_BAD_REQUEST)
