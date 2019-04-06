from rest_framework import serializers

from agreements.models import Agreement, AgreementToUser


class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = '__all__'


class AgreementListSerializer(serializers.ModelSerializer):
    receivers_count = serializers.SerializerMethodField()

    class Meta:
        model = Agreement
        fields = ('id', 'title', 'receivers_count', 'creation_date', 'update_date')

    def get_receivers_count(self, instance):
        return instance.targeted_users.count()


class AgreementToUserSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = AgreementToUser
        fields = ('user', 'datetime')

    def get_user(self, instance):
        user = instance.user
        return '%s %s' % (user.first_name, user.last_name)
