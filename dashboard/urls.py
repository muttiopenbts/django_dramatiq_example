from django.conf.urls import url
from django.urls import include, path, re_path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'dashboard'

urlpatterns = [
    re_path(r'^$', views.HomeView.as_view(), name='home'),
    re_path(r'^$', views.HomeView.as_view(), name='index'),
    re_path(r'^jobs_list/$', views.IndexView.as_view(), name='jobs_list'),
    re_path(r'^add/$', views.JobCreate.as_view(), name='post_job_new'),
    path('accounts/', include('django.contrib.auth.urls')),
]
