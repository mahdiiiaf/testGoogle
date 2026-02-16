from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, JobViewSet, ProposalViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet)
router.register(r'proposals', ProposalViewSet)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('', include(router.urls)),
]
