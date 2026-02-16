from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Job, Proposal

User = get_user_model()

class UserAccountTests(APITestCase):
    def test_register_company(self):
        url = reverse('register')
        data = {
            'username': 'testcompany',
            'password': 'password123',
            'role': 'COMPANY',
            'company_profile': {
                'company_name': 'Test Company',
                'description': 'Testing'
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().role, 'COMPANY')
        self.assertEqual(User.objects.get().company_profile.company_name, 'Test Company')

    def test_register_freelancer(self):
        url = reverse('register')
        data = {
            'username': 'testfreelancer',
            'password': 'password123',
            'role': 'FREELANCER',
            'freelancer_profile': {
                'skills': 'Python, Django',
                'hourly_rate': '50.00',
                'bio': 'I am a dev'
            }
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username='testfreelancer').role, 'FREELANCER')

class JobProposalTests(APITestCase):
    def setUp(self):
        self.company_user = User.objects.create_user(username='company', password='password', role='COMPANY')
        self.freelancer_user = User.objects.create_user(username='freelancer', password='password', role='FREELANCER')
        self.expert_user = User.objects.create_user(username='expert', password='password', role='EXPERT')

    def test_company_can_post_job(self):
        self.client.force_authenticate(user=self.company_user)
        url = reverse('job-list')
        data = {'title': 'New Job', 'description': 'Do work', 'budget': '1000.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Job.objects.count(), 1)

    def test_freelancer_cannot_post_job(self):
        self.client.force_authenticate(user=self.freelancer_user)
        url = reverse('job-list')
        data = {'title': 'New Job', 'description': 'Do work', 'budget': '1000.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_freelancer_can_bid_on_job(self):
        job = Job.objects.create(company=self.company_user, title='Job', description='Desc', budget=500)
        self.client.force_authenticate(user=self.freelancer_user)
        url = reverse('proposal-list')
        data = {'job': job.id, 'cover_letter': 'I can do it', 'bid_amount': '450.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Proposal.objects.count(), 1)
        self.assertEqual(Proposal.objects.get().applicant, self.freelancer_user)

    def test_expert_can_bid_on_job(self):
        job = Job.objects.create(company=self.company_user, title='Job', description='Desc', budget=500)
        self.client.force_authenticate(user=self.expert_user)
        url = reverse('proposal-list')
        data = {'job': job.id, 'cover_letter': 'I am an expert', 'bid_amount': '600.00'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Proposal.objects.filter(applicant=self.expert_user).count(), 1)
