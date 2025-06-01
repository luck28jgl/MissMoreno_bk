from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from core.views import ApigetUserType
from core import views
from core.views import *

router = routers.DefaultRouter()
router.register(r'usuarios', UsuariosViewSet)
router.register(r'bocabulario', bocabularioViewSet)
router.register(r'abcedario', abcedarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('obtener-tipo-usuario/', ApigetUserType.as_view()),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)