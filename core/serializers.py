from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ExpertProfile, CompanyProfile, FreelancerProfile, Job, Proposal

User = get_user_model()

class ExpertProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertProfile
        fields = ['skills', 'hourly_rate', 'bio']

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'website', 'description']

class FreelancerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerProfile
        fields = ['skills', 'hourly_rate', 'bio']

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    expert_profile = ExpertProfileSerializer(required=False)
    company_profile = CompanyProfileSerializer(required=False)
    freelancer_profile = FreelancerProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role', 'expert_profile', 'company_profile', 'freelancer_profile']

    def create(self, validated_data):
        role = validated_data.get('role')
        expert_data = validated_data.pop('expert_profile', None)
        company_data = validated_data.pop('company_profile', None)
        freelancer_data = validated_data.pop('freelancer_profile', None)

        user = User.objects.create_user(**validated_data)

        if role == 'EXPERT' and expert_data:
            ExpertProfile.objects.create(user=user, **expert_data)
        elif role == 'COMPANY' and company_data:
            CompanyProfile.objects.create(user=user, **company_data)
        elif role == 'FREELANCER' and freelancer_data:
            FreelancerProfile.objects.create(user=user, **freelancer_data)

        return user

class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='company.company_profile.company_name')

    class Meta:
        model = Job
        fields = ['id', 'company', 'company_name', 'title', 'description', 'budget', 'created_at']
        read_only_fields = ['company']

class ProposalSerializer(serializers.ModelSerializer):
    applicant_username = serializers.ReadOnlyField(source='applicant.username')

    class Meta:
        model = Proposal
        fields = ['id', 'job', 'applicant', 'applicant_username', 'cover_letter', 'bid_amount', 'created_at']
        read_only_fields = ['applicant']
