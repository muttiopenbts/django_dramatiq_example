from django.contrib.auth.models import User, Group
from dashboard.models import Job
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer, JobSerializer
from django.contrib.auth.mixins import LoginRequiredMixin


class UserViewSet(LoginRequiredMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(LoginRequiredMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class JobViewSet(LoginRequiredMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows jobs to be viewed or edited.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
