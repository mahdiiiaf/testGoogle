from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from .views import UserRegistrationView, JobViewSet, ProposalViewSet, home, job_detail, register_view, dashboard, post_job, submit_proposal, profile_view

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
    path('register/', register_view, name='web-register'),
    path('login/', auth_views.LoginView.as_view(template_name='roshd/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='web-home'), name='logout'),
    path('dashboard/', dashboard, name='web-dashboard'),
    path('job/new/', post_job, name='web-post-job'),
    path('job/<int:pk>/apply/', submit_proposal, name='web-submit-proposal'),
    path('profile/<str:username>/', profile_view, name='web-profile'),
]
