from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import CoreTodoGroupViewSet, CoreTodoViewSet, RegisterView

router = DefaultRouter()
router.register(r"groups", CoreTodoGroupViewSet, basename="core_todo_group")
router.register(r"todos", CoreTodoViewSet, basename="core_todo")

urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterView.as_view(), name="register"),
    path("", include(router.urls)),
]
