from rest_framework import serializers
from .models import Branch, User, Student, Room, Course, Group, Enrollment, Payment

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        exclude = ('created_at', 'is_active')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'role', 'branch', 'first_name', 'last_name', 'is_active')

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ('created_at', 'is_active')

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        exclude = ('created_at', 'is_active')

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ('created_at', 'is_active')

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        exclude = ('created_at', 'is_active')

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        exclude = ('created_at', 'is_active')

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ('created_at', 'is_active')
