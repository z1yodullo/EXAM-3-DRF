from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,CreateAPIView,RetrieveUpdateAPIView,RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count,Avg,Sum,Q,Case,When,FloatField
import subprocess
import sys
from .models import *
from .serializers import *
from .permissions import *

TIME_LIMIT = 2


class Register(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MyProfile(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        profile, created = Profile.objects.get_or_create(
            user_id=self.request.user,
            defaults={'nickname': self.request.user.username}
        )
        return profile


class Courses(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['title']
    search_fields = ['title']
    ordering_fields = ['id', 'title', 'cr_at']
    ordering = ['id']


class CourseDetail(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.prefetch_related('modules')
    serializer_class = CourseDetailSerializer
    permission_classes = [IsAdminOrReadOnly]


class Modules(ListCreateAPIView):
    queryset = Module.objects.select_related('course_id')
    serializer_class = ModuleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['course_id']
    search_fields = ['title']
    ordering_fields = ['id', 'title', 'cr_at']
    ordering = ['id']


class ModuleDetail(RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.select_related('course_id').prefetch_related('tasks')
    serializer_class = ModuleDetailSerializer
    permission_classes = [IsAdminOrReadOnly]


class Tasks(ListCreateAPIView):
    queryset = Task.objects.select_related('module_id')
    serializer_class = TaskSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['module_id']
    search_fields = ['title', 'description']
    ordering_fields = ['id', 'title', 'cr_at']
    ordering = ['id']


class TaskDetail(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.select_related('module_id')
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAdminOrReadOnly]


class TestCases(ListCreateAPIView):
    queryset = TestCase.objects.select_related('task_id')
    serializer_class = TestCaseSerializer
    permission_classes = [IsAdmin]
    filterset_fields = ['task_id']
    ordering = ['id']


class TestCaseDetail(RetrieveUpdateDestroyAPIView):
    queryset = TestCase.objects.select_related('task_id')
    serializer_class = TestCaseSerializer
    permission_classes = [IsAdmin]


def check_code(code, test_cases):
    for test_case in test_cases:
        try:
            result = subprocess.run(
                [sys.executable, "-c", code],
                input=test_case.input_data,
                text=True,
                capture_output=True,
                timeout=TIME_LIMIT,
            )
        except subprocess.TimeoutExpired:
            return 'time_limit'

        if result.returncode != 0:
            return 'error'

        if result.stdout.strip() != test_case.expected_output.strip():
            return 'wrong_answer'

    return 'accepted'


class Submissions(ListCreateAPIView):
    serializer_class = SubmissionSerializer
    filterset_fields = ['task', 'status']
    ordering_fields = ['id', 'cr_at']
    ordering = ['id']

    def get_queryset(self):
        submissions = Submission.objects.select_related('user', 'task')
        if self.request.user.role == 'admin':
            return submissions
        return submissions.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        data = request.data
        if 'task_id' not in data or 'code' not in data:
            return Response({'detail': 'task_id and code are required'}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(Task, pk=data['task_id'])
        test_cases = TestCase.objects.filter(task_id=task.pk)
        if not test_cases.exists():
            return Response({'detail': 'This task has no test cases'}, status=status.HTTP_400_BAD_REQUEST)

        result = check_code(data['code'], test_cases)
        submission = Submission.objects.create(user=request.user, task=task, code=data['code'], status=result)
        return Response(SubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)


class SubmissionDetail(RetrieveAPIView):
    queryset = Submission.objects.select_related('user', 'task')
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]


class CourseStats(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        courses = Course.objects.annotate(
            tasks_count=Count('modules__tasks')
        ).values('id', 'title', 'tasks_count')
        return Response(list(courses))


class UserStats(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.annotate(
            submissions_count=Count('submissions'),
            accepted_count=Count('submissions', filter=Q(submissions__status='accepted'))
        ).values('id', 'username', 'submissions_count', 'accepted_count')
        return Response(list(users))


class TopUsers(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = User.objects.annotate(
            accepted_count=Count('submissions', filter=Q(submissions__status='accepted'))
        ).order_by('-accepted_count')[:10].values('id', 'username', 'accepted_count')
        return Response(list(users))


class PopularCourses(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        courses = Course.objects.annotate(
            submissions_count=Count('modules__tasks__submissions')
        ).order_by('-submissions_count')[:5].values('id', 'title', 'submissions_count')
        return Response(list(courses))


class HardTasks(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        tasks = Task.objects.annotate(
            submissions_count=Count('submissions'),
            accept_rate=Avg(Case(
                When(submissions__status='accepted', then=1),
                default=0,
                output_field=FloatField()
            ))
        ).filter(submissions_count__gt=0).order_by('accept_rate')[:10].values(
            'id', 'title', 'submissions_count', 'accept_rate'
        )
        return Response(list(tasks))


class PlatformStats(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        submissions = Submission.objects.aggregate(
            total_submissions=Count('id'),
            accepted_submissions=Count('id', filter=Q(status='accepted'))
        )
        tasks = Course.objects.annotate(
            tasks_count=Count('modules__tasks')
        ).aggregate(
            total_tasks=Sum('tasks_count', default=0),
            avg_tasks_per_course=Avg('tasks_count')
        )
        stats = {
            'total_users': User.objects.count(),
            'total_courses': Course.objects.count(),
        }
        stats.update(tasks)
        stats.update(submissions)
        return Response(stats)
