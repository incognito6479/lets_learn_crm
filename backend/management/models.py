from django.db import models
from django.contrib.auth.models import AbstractUser

class Branch(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
        ('CEO', 'CEO'),
        ('teacher', 'Teacher'),
        ('superuser', 'Superuser'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)

class Student(models.Model):
    full_name = models.CharField(max_length=255)
    phone1 = models.CharField(max_length=20)
    phone2 = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.full_name

class Room(models.Model):
    name = models.CharField(max_length=255)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='rooms')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.branch.name})"

class Course(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Group(models.Model):
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField(Student, through='Enrollment', related_name='groups')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    started_at = models.DateField()
    starts_at = models.TimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Enrollment(models.Model):
    STATUS_CHOICES = (
        ('enrolled', 'Enrolled'),
        ('finished', 'Finished'),
        ('dropped', 'Dropped'),
    )
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')

    class Meta:
        unique_together = ('student', 'group')

class Payment(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.amount}"
