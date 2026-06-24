from rest_framework import viewsets, permissions
from django.utils import timezone
from django.db.models import Sum
from rest_framework.exceptions import ValidationError
from .models import Enrollment
from .models import Branch, User, Student, Room, Course, Group, Enrollment, Payment, Grade, Absence
from .serializers import (
    BranchSerializer, UserSerializer, StudentSerializer, 
    RoomSerializer, CourseSerializer, GroupSerializer, 
    EnrollmentSerializer, PaymentSerializer, GradeSerializer, AbsenceSerializer
)

class SoftDeleteModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.queryset.filter(is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

class BranchViewSet(SoftDeleteModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer

class UserViewSet(SoftDeleteModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.queryset.all()

class StudentViewSet(SoftDeleteModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

class RoomViewSet(SoftDeleteModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class CourseViewSet(SoftDeleteModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class GroupViewSet(SoftDeleteModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def perform_update(self, serializer):
        instance = self.get_object()
        new_status = serializer.validated_data.get('status', instance.status)
        
        if new_status == 'finished' and instance.status != 'finished':
            has_debt = Enrollment.objects.filter(
                group=instance,
                status='enrolled',
                payment_status='debt'
            ).exists()
            if has_debt:
                raise ValidationError("Cannot finish group because some enrolled students have outstanding debt.")
        
        group = serializer.save()
        
        if group.status == 'finished' and instance.status != 'finished':
            Enrollment.objects.filter(group=group, status='enrolled').update(status='finished')

class EnrollmentViewSet(SoftDeleteModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def perform_destroy(self, instance):
        instance.status = 'dropped'
        instance.save()

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        payment = serializer.save()
        enrollment = Enrollment.objects.filter(
            student=payment.student,
            group=payment.group,
            is_active=True
        ).first()
        if enrollment:
            enrollment.check_debt()

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = 'canceled'
        instance.save()

class GradeViewSet(SoftDeleteModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer

class AbsenceViewSet(SoftDeleteModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer
