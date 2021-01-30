import debug_toolbar
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import include, path, re_path
from dashboard import views

urlpatterns = [
    re_path(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^', include('dashboard.urls')),
    url(r'^', include('api.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
]
