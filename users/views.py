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

from .serializers import RegisterSerializer, LoginSerializer,UsernameCheckSerializer,UserSerializer,ProfileUpdateSerializer,PasswordChangeSerializer
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
    