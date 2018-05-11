from django.conf.urls import url
from django.urls import include, path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'dashboard'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^add/$', views.JobCreate.as_view(), name='post_job_new'),
    path('accounts/', include('django.contrib.auth.urls')),
]
