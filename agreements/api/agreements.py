from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from agreements.models import Agreement, AgreementToUser
from agreements.serializers import AgreementSerializer, AgreementToUserSerializer, AgreementListSerializer
from g_utils.rest import SearchMixin


class AgreementApiView(viewsets.ModelViewSet, SearchMixin):
    serializer_class = AgreementSerializer
    queryset = Agreement.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AgreementListSerializer
        else:
            return self.serializer_class

    @action(detail=False, methods=['get'])
    def pending(self, request):
        agreements = Agreement.objects.filter(targeted_users=self.request.user)
        agreements = agreements.exclude(users=self.request.user)
        serializer = self.get_serializer(agreements, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def confirmed_by(self, request):
        agreement = self.get_object()
        users = AgreementToUser.objects.filter(agreement=agreement)
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        agreement = self.get_object()
        AgreementToUser.objects.create(user=request.user, agreement=agreement)
        return Response(status=status.HTTP_200_OK)


class AgreementToUserApiView(viewsets.ModelViewSet, SearchMixin):
    serializer_class = AgreementToUserSerializer
    queryset = AgreementToUser.objects.all()
    fields_mapping = {'user': 'user__last_name'}

    def get_queryset(self):
        queryset = super(AgreementToUserApiView, self).get_queryset()
        return queryset.filter(agreement__id=self.request.GET['agreement'])
