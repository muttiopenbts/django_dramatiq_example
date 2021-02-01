from django.contrib.auth.models import User, Group
from dashboard.models import Job, Rpc
from rest_framework import serializers
from dashboard.tasks import process_job, process_rpc


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
        fields = ('output', 'id', 'cmd_list', 'user', 'signature')
        depth = 0

    def create(self, validated_data):
        # Save job record
        job = Job.objects.create(**validated_data)
        # Pass job to be queue to be picked up and processed by agent.
        process_job.send(job.id)
        return job

class RpcSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rpc
        fields = ('rpc', 'params', 'signature', 'timestamp',)
        depth = 0

    def create(self, validated_data):
        # Save job record
        rpc = Rpc.objects.create(**validated_data)
        # Pass job to be queue to be picked up and processed by agent.
        process_rpc.send(rpc.id)
        return rpc
