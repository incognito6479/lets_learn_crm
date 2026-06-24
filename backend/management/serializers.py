from rest_framework import serializers
from .models import Branch, User, Student, Room, Course, Group, Enrollment, Payment, Grade, Absence

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        exclude = ('created_at', 'is_active')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'role', 'branch', 'first_name', 'last_name', 'is_active', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

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
        read_only_fields = ('debt_amount',)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ('created_at',)

class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grade
        exclude = ('created_at',)

    def validate(self, attrs):
        enrolled_student = attrs.get('enrolled_student')
        group = attrs.get('group')
        grade = attrs.get('grade')

        if grade is not None and (grade < 0 or grade > 5):
            raise serializers.ValidationError({"grade": "Grade must be between 0 and 5."})

        if enrolled_student and group:
            enrollment_exists = Enrollment.objects.filter(
                student=enrolled_student,
                group=group,
                is_active=True
            ).exists()
            if not enrollment_exists:
                raise serializers.ValidationError({
                    "enrolled_student": f"Student is not actively enrolled in the specified group."
                })

        return attrs

class AbsenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Absence
        exclude = ('created_at',)

    def validate(self, attrs):
        student = attrs.get('student')
        group = attrs.get('group')

        if student and group:
            enrollment_exists = Enrollment.objects.filter(
                student=student,
                group=group,
                is_active=True
            ).exists()
            if not enrollment_exists:
                raise serializers.ValidationError({
                    "student": "Student is not actively enrolled in the specified group."
                })

        return attrs
