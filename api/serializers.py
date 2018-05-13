from django.contrib.auth.models import User, Group
from dashboard.models import Job
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')
        depth = 1

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')
        depth = 1

class JobSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Job
        fields = ('get_output', 'id', 'cmd_list', 'user', 'signature')
        depth = 0

    def create(self, validated_data):
            return Job.objects.create(**validated_data)
