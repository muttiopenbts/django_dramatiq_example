from django.contrib.auth.models import User, Group
from dashboard.models import Job
from rest_framework import viewsets
from .serializers import UserSerializer, GroupSerializer, JobSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import renderers
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class JobViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows jobs to be viewed or edited.
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer],methods='POST')
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def perform_create(self, serializer):
        # Save the user that submitted the job request
        serializer.save(user=self.request.user)
