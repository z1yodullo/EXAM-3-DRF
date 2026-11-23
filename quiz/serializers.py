from rest_framework import serializers 
from .models import *


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','username','password']
        extra_kwargs={'password':{'write_only':True}}

    def create(self, validated_data):
        user=User.objects.create_user(**validated_data)
        Profile.objects.create(user_id=user,nickname=user.username)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=Profile
        fields='__all__'
        read_only_fields=['user_id','cr_at']


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model=Task
        fields='__all__'
        read_only_fields=['cr_at']


class TaskDetailSerializer(serializers.ModelSerializer):
    is_solved_by_me=serializers.SerializerMethodField()

    class Meta:
        model=Task
        fields='__all__'
        read_only_fields=['cr_at']

    def get_is_solved_by_me(self, obj):
        user=self.context['request'].user
        return Submission.objects.filter(user=user,task=obj,status='accepted').exists()


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Module
        fields='__all__'
        read_only_fields=['cr_at']


class ModuleDetailSerializer(serializers.ModelSerializer):
    tasks=TaskSerializer(many=True,read_only=True)

    class Meta:
        model=Module
        fields='__all__'
        read_only_fields=['cr_at']


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model=Course
        fields='__all__'
        read_only_fields=['cr_at']


class CourseDetailSerializer(serializers.ModelSerializer):
    modules=ModuleSerializer(many=True,read_only=True)

    class Meta:
        model=Course
        fields='__all__'
        read_only_fields=['cr_at']


class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model=TestCase
        fields='__all__'


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Submission
        fields='__all__'
        read_only_fields=['user','status','cr_at']
