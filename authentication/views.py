from django.shortcuts import render
from .models import User,TemporaryUser
from .serializers import UserSerializer,PrivateUserSerializer,TemporaryUserSerializer
from rest_framework import viewsets,status
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth.hashers import check_password
from phonenumbers import parse, is_valid_number, PhoneNumber
from phonenumbers.phonenumberutil import region_code_for_number
from django.utils import timezone
import hashlib
import requests
import json

class UserViewSets(viewsets.ModelViewSet):
    class_serializer = UserSerializer
    def signin(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')

        try:
            user = User.objects.get(
                Q(email=username) | Q(username=username)
            )
        except User.DoesNotExist:
            detail = 'Authentication credentials are not correct.'
            return Response(data={'detail': detail}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if check_password(password, user.password):
            serializer = PrivateUserSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            detail = 'Authentication credentials are not correct.'
            return Response(data={'detail': detail}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def logout(self, request):
        # Effacer le token côté client
        response = Response({"detail": "Déconnexion réussie"}, status=status.HTTP_200_OK)
        response.delete_cookie("auth_token")
        return response

    def signup(self,request):
        
        phone_number = request.data.get('phone_number')
        try:
            phone = parse(phone_number)
        except:
            phone =PhoneNumber()

        if not is_valid_number(phone):
            detail = 'Le numéro de téléphone est invalide'
            return Response({'detail': detail}, status=status.HTTP_406_NOT_ACCEPTABLE)
        
        if User.objects.filter(phone_number=phone_number).exists():
            detail = 'un compte avec le meme numéro de téléphone existe'
            return Response({'detail': detail}, status=status.HTTP_406_NOT_ACCEPTABLE) 
        
        if TemporaryUser.objects.filter(phone_number=phone_number).exists():
            tmpuser = TemporaryUser.objects.get(phone_number=phone_number)
            diff = timezone.now() - tmpuser.record_at
            if diff.seconds / 60 < 3:
                detail = 'The code has already been sent to this number. please try again after 3 minutes'
                return Response({'detail': detail}, status=status.HTTP_406_NOT_ACCEPTABLE)
            otp =self.generate_otp()
            check_otp =self.send_sms(otp,phone_number)
            if not check_otp:
                detail = "erreur de transmition de l'otp"
                return Response({'detail': detail}, status=status.HTTP_406_NOT_ACCEPTABLE)
            tmpuser.otp = hashlib.sha256(str(otp).encode('utf-8')).hexdigest()
            tmpuser.record_at = timezone.now()
            tmpuser.bad_code_count = 0
            tmpuser.bad_code_init_time = timezone.now()
            tmpuser.save()
            serializer = TemporaryUserSerializer(tmpuser ,context={'request': request})
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else :
            otp =self.generate_otp()
            if not self.send_sms(otp,phone_number):
                detail = "erreur de transmition de l'otp"
                return Response({'detail': detail}, status=status.HTTP_406_NOT_ACCEPTABLE)
            
            tmpuser = TemporaryUser.objects.create(phone_number=phone_number,record_at = timezone.now(), otp=hashlib.sha256(str(otp).encode('utf-8')).hexdigest())
            tmpuser.save()
            # Send SMS to the User.
            serializer = TemporaryUserSerializer(tmpuser ,context={'request': request})
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


    def validate_signup(self,request):
        
        phone_number = request.data.get("phone_number")
        otp = request.data.get("otp")
        if TemporaryUser.objects.filter(phone_number=phone_number).exists():
            tmpuser = TemporaryUser.objects.get(phone_number=phone_number)
            old_otp = tmpuser.otp
            diff = timezone.now() - tmpuser.record_at
            
            if diff.seconds / 60 > 1:
                detail = 'Délai dépassé'
                return Response({'detail': detail}, status=status.HTTP_406_NOT_ACCEPTABLE) 
            
            if not old_otp == hashlib.sha256(str(otp).encode('utf-8')).hexdigest():
                detail = 'code erroné'
                return Response({'detail': detail}, status=status.HTTP_406_NOT_ACCEPTABLE) 
            
            user = User.objects.create(username=phone_number,phone_number=phone_number)

            tmpuser.delete()
            serializer = UserSerializer(user,context={'request': request})
            return Response(serializer.data,status=status.HTTP_202_ACCEPTED)
        else:
            detail = "Le numéro demandé n'est plus attribué"
            return Response({"detail":detail},status=status.HTTP_406_NOT_ACCEPTABLE)




    
    def generate_otp(self):
        import random
        otp = random.randint(100000, 999999)
        return otp
    
    
    def send_sms(self,otp, number):
        url =  'https://api.requeta.com/sms/'
        access_token = "c1cdaaca76b695b5bd43c3a49480cf996d2d4530"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Token {access_token}',
        }
        data = json.dumps({
                "sender": "Modernexus",
                "phone": number,
                "body": "votre code de confirmation est "+ str(otp)
            }) 
        res = requests.post(url,data=data,headers=headers)
        data = res.json()
        print("data>>>",data)    
        if data["status"] == "Success":
            return True
        return False
    
