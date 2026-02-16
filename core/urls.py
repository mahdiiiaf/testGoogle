from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, JobViewSet, ProposalViewSet, home, job_detail

router = DefaultRouter()
router.register(r'jobs', JobViewSet)
router.register(r'proposals', ProposalViewSet)

urlpatterns = [
    # API
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('api/', include(router.urls)),

    # Website
    path('', home, name='web-home'),
    path('job/<int:pk>/', job_detail, name='web-job-detail'),
]
