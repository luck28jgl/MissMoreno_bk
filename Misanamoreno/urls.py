from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers
from django.conf import settings
from core.views import ApigetUserType
from core.views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('api/v1/token/login/', CustomTokenCreateView.as_view(), name='custom-token-create'),
    path('api/v1/token/logout/', LogoutView.as_view(), name='custom-token-create'),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('obtener-tipo-usuario/', ApigetUserType.as_view()),
    path('api/v1/core/', include('core.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)