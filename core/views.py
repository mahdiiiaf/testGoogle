from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Job, Proposal
from .serializers import UserSerializer, JobSerializer, ProposalSerializer
from .permissions import IsCompany, IsFreelancerOrExpert, IsOwnerOrReadOnly

User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsCompany]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(company=self.request.user)

class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsFreelancerOrExpert]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)
