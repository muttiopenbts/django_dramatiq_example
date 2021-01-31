from django.conf.urls import url, include
from rest_framework import routers
from . import views
from rest_framework.schemas import get_schema_view
from rest_framework.authtoken import views as auth_views

schema_view = get_schema_view(title='Cascade API')

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'jobs', views.JobViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'rpc', views.RpcViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', auth_views.obtain_auth_token),
    url(r'^schema/$', schema_view),
]
