from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns=[
    path('register/', views.Register.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('profile/', views.MyProfile.as_view()),
    path('courses/', views.Courses.as_view()),
    path('courses/<int:pk>/', views.CourseDetail.as_view()),
    path('modules/', views.Modules.as_view()),
    path('modules/<int:pk>/', views.ModuleDetail.as_view()),
    path('tasks/', views.Tasks.as_view()),
    path('tasks/<int:pk>/', views.TaskDetail.as_view()),
    path('test-cases/', views.TestCases.as_view()),
    path('test-cases/<int:pk>/', views.TestCaseDetail.as_view()),
    path('submissions/', views.Submissions.as_view()),
    path('submissions/<int:pk>/', views.SubmissionDetail.as_view()),
    path('stats/courses/', views.CourseStats.as_view()),
    path('stats/users/', views.UserStats.as_view()),
    path('stats/top-users/', views.TopUsers.as_view()),
    path('stats/popular-courses/', views.PopularCourses.as_view()),
    path('stats/hard-tasks/', views.HardTasks.as_view()),
    path('stats/platform/', views.PlatformStats.as_view()),
]
