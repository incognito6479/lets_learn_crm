from rest_framework import viewsets, permissions
from .models import Branch, User, Student, Room, Course, Group, Enrollment, Payment
from .serializers import (
    BranchSerializer, UserSerializer, StudentSerializer, 
    RoomSerializer, CourseSerializer, GroupSerializer, 
    EnrollmentSerializer, PaymentSerializer
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
        return self.queryset

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

class EnrollmentViewSet(SoftDeleteModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer

    def perform_destroy(self, instance):
        instance.status = 'dropped'
        instance.save()

class PaymentViewSet(SoftDeleteModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
