from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import Job, Proposal, Message
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

# Website Views
def home(request):
    jobs = Job.objects.all().order_by('-created_at')
    return render(request, 'roshd/home.html', {'jobs': jobs})

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    return render(request, 'roshd/job_detail.html', {'job': job})

def register_view(request):
    if request.method == 'POST':
        # Simple registration logic for demonstration
        # In a real app, use Django Forms
        data = request.POST
        username = data.get('username')
        password = data.get('password')
        role = data.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'نام کاربری قبلاً انتخاب شده است.')
        else:
            user = User.objects.create_user(username=username, password=password, role=role)
            login(request, user)
            messages.success(request, f'خوش آمدید، {username}!')
            return redirect('web-dashboard')

    return render(request, 'roshd/auth/register.html')

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}

    if user.role == 'COMPANY':
        context['jobs'] = Job.objects.filter(company=user).order_by('-created_at')
    else:
        context['proposals'] = Proposal.objects.filter(applicant=user).order_by('-created_at')

    return render(request, 'roshd/dashboard.html', context)

@login_required
def post_job(request):
    if request.user.role != 'COMPANY':
        messages.error(request, 'فقط شرکت‌ها می‌توانند آگهی ثبت کنند.')
        return redirect('web-dashboard')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        budget = request.POST.get('budget')

        Job.objects.create(
            company=request.user,
            title=title,
            description=description,
            budget=budget
        )
        messages.success(request, 'آگهی شما با موفقیت ثبت شد.')
        return redirect('web-dashboard')

    return render(request, 'roshd/post_job.html')

@login_required
def submit_proposal(request, pk):
    if request.user.role not in ['FREELANCER', 'EXPERT']:
        messages.error(request, 'فقط متخصصان و فریلنسرها می‌توانند پیشنهاد ارسال کنند.')
        return redirect('web-job-detail', pk=pk)

    job = get_object_or_404(Job, pk=pk)

    if request.method == 'POST':
        cover_letter = request.POST.get('cover_letter')
        bid_amount = request.POST.get('bid_amount')

        Proposal.objects.create(
            job=job,
            applicant=request.user,
            cover_letter=cover_letter,
            bid_amount=bid_amount
        )
        messages.success(request, 'پیشنهاد شما با موفقیت ارسال شد.')
        return redirect('web-dashboard')

    return render(request, 'roshd/submit_proposal.html', {'job': job})

@login_required
def view_proposals(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.company != request.user:
        messages.error(request, 'شما اجازه مشاهده پیشنهادات این آگهی را ندارید.')
        return redirect('web-dashboard')

    proposals = job.proposals.all().order_by('-created_at')
    return render(request, 'roshd/view_proposals.html', {'job': job, 'proposals': proposals})

def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    context = {'profile_user': profile_user}

    if profile_user.role == 'EXPERT':
        context['profile'] = getattr(profile_user, 'expert_profile', None)
    elif profile_user.role == 'FREELANCER':
        context['profile'] = getattr(profile_user, 'freelancer_profile', None)
    elif profile_user.role == 'COMPANY':
        context['profile'] = getattr(profile_user, 'company_profile', None)

    return render(request, 'roshd/profile.html', context)

@login_required
def chat_list(request):
    # Get all users the current user has messaged or received messages from
    sent_to = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received_from = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    user_ids = set(list(sent_to) + list(received_from))
    users = User.objects.filter(id__in=user_ids)
    return render(request, 'roshd/chat_list.html', {'chat_users': users})

@login_required
def chat_detail(request, username):
    other_user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=other_user, content=content)
            return redirect('web-chat', username=username)

    messages_list = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('created_at')

    return render(request, 'roshd/chat_detail.html', {
        'other_user': other_user,
        'chat_messages': messages_list
    })
