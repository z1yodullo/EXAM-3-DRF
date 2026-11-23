from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    roles = (
        ('admin', "ADMIN"),
        ('student', "STUDENT"),
    )

    role=models.CharField(max_length=20, choices=roles, default='student')
    cr_at=models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role='admin'
        super().save(*args, **kwargs)


class Profile(models.Model):
    nickname=models.CharField(max_length=254)
    ava=models.CharField(max_length=255, blank=True)
    user_id=models.OneToOneField(User,on_delete=models.CASCADE)
    cr_at=models.DateTimeField(auto_now_add=True)


class Course(models.Model):
    title=models.CharField(max_length=255)
    cr_at=models.DateTimeField(auto_now_add=True)


class Module(models.Model):
    title=models.CharField(max_length=255)
    course_id=models.ForeignKey(Course,on_delete=models.CASCADE,related_name='modules')
    cr_at=models.DateTimeField(auto_now_add=True)


class Task(models.Model):
    title=models.CharField(max_length=255)
    description=models.TextField()
    module_id=models.ForeignKey(Module,on_delete=models.CASCADE,related_name='tasks')
    cr_at=models.DateTimeField(auto_now_add=True)


class TestCase(models.Model):
    task_id=models.ForeignKey(Task,on_delete=models.CASCADE,related_name='test_cases')
    input_data = models.TextField(blank=True)
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=False)
    cr_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Test #{self.pk} for {self.task_id}"


class Submission(models.Model):

    statuses = (
        ('accepted', "ACCEPTED"),
        ('wrong_answer', "WRONG_ANSWER"),
        ('error', "ERROR"),
        ('time_limit', "TIME_LIMIT"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    code = models.TextField()
    status = models.CharField(max_length=20, choices=statuses)
    cr_at = models.DateTimeField(auto_now_add=True)
