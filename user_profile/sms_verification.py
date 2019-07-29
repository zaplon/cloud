import urllib
from datetime import datetime, timedelta
import random

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_auth.app_settings import create_token
from rest_auth.models import TokenModel
from rest_auth.serializers import LoginSerializer, JWTSerializer, TokenSerializer
from rest_auth.utils import jwt_encode
from rest_auth.views import LoginView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from django_redis import get_redis_connection

from g_utils.utils import send_sms
from user_profile.models import MobileCode
from django.conf import settings


def send_verification_code(user):
    code = MobileCode.objects.create(user=user, code=random.randint(100000, 999999))
    message = f'Hasło weryfikacyjne do systemu Gabinet ważne przez 15 minut: {code.code}'
    send_sms(user.profile.mobile, message)


redis = get_redis_connection()


class GabinetLoginView(LoginView):

    def post(self, request):
        if not settings.SMS_VERIFICATION:
            return super(GabinetLoginView, self).post(request)
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        user = self.serializer.validated_data['user']
        secret = random.randint(0, 10000)
        redis.set('sms:%s' % secret, user.id)
        if not user.profile.mobile:
            return Response(status=200, data={'secret': secret, 'set_mobile': 1})
        send_verification_code(user)
        return Response(status=200, data={'secret': secret})


class SMSValidationView(LoginView):

    def post(self, request):
        now = datetime.now()
        try:
            code = request.data['code']
            user_id = redis.get('sms:%s' % request.data['secret'])
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        mobile_codes = MobileCode.objects.filter(user_id=user_id, code=code, creation_date__gte=now-timedelta(minutes=15))
        if not mobile_codes.exists():
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        self.user = User.objects.get(id=user_id)
        if getattr(settings, 'REST_USE_JWT', False):
            self.token = jwt_encode(self.user)
        else:
            self.token = create_token(self.token_model, self.user, None)
        if getattr(settings, 'REST_SESSION_LOGIN', True):
            login(request, self.user)
        return self.get_response()


class SMSCodeViewSet(ViewSet):
    permission_classes = (AllowAny,)

    @action(detail=False, methods=['post'])
    def resend_code(self, request):
        try:
            user_id = redis.get('sms:%s' % request.data['secret'])
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        send_verification_code(User.objects.get(id=user_id))
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def add_mobile(self, request):
        try:
            user_id = redis.get('sms:%s' % request.data['secret'])
            mobile = request.data['mobile']
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=user_id)
        user.profile.mobile = mobile
        user.profile.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def send_to_email(self, request):
        try:
            user_id = redis.get('sms:%s' % request.data['secret'])
        except KeyError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.get(id=user_id)
        code = MobileCode.objects.create(user=user, code=random.randint(100000, 999999))
        send_mail(u'Jednorazowe hasło do programu Gabinet', str(code.code), 'noreply@gabinet.online',
            [user.profile.email],
            fail_silently=False,
        )
        return Response(status=status.HTTP_200_OK)
