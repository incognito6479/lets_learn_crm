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
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class SoftDeleteModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.queryset.filter(is_active=True)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()


class IsAdminOrCEOOrSuperuserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ['admin', 'CEO', 'superuser'] or request.user.is_superuser

class IsAdminOrCEOOrSuperuserOrSelf(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ['admin', 'CEO', 'superuser'] or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.id == obj.id:
            return True
        return request.user.role in ['admin', 'CEO', 'superuser'] or request.user.is_superuser

class IsCashierOrAdminOrCEOOrSuperuserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role in ['admin', 'CEO', 'superuser', 'cashier'] or request.user.is_superuser

class IsCashierOrAdminOrCEOOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'CEO', 'superuser', 'cashier'] or request.user.is_superuser

class IsTeacherOrAdminOrCEOOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.role in ['admin', 'CEO', 'superuser', 'teacher'] or request.user.is_superuser

class BranchViewSet(SoftDeleteModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer
    permission_classes = [IsAdminOrCEOOrSuperuserOrReadOnly]

class UserViewSet(SoftDeleteModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrCEOOrSuperuserOrSelf]

    def get_queryset(self):
        return self.queryset.all()

class StudentViewSet(SoftDeleteModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsCashierOrAdminOrCEOOrSuperuserOrReadOnly]

class RoomViewSet(SoftDeleteModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAdminOrCEOOrSuperuserOrReadOnly]

class CourseViewSet(SoftDeleteModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrCEOOrSuperuserOrReadOnly]

class GroupViewSet(SoftDeleteModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrCEOOrSuperuserOrReadOnly]

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
    permission_classes = [IsCashierOrAdminOrCEOOrSuperuserOrReadOnly]

    def perform_destroy(self, instance):
        instance.status = 'dropped'
        instance.save()

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsCashierOrAdminOrCEOOrSuperuser]

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
    permission_classes = [IsTeacherOrAdminOrCEOOrSuperuser]

class AbsenceViewSet(SoftDeleteModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer
    permission_classes = [IsTeacherOrAdminOrCEOOrSuperuser]

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        token['user_id'] = user.id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['user_id'] = self.user.id
        data['username'] = self.user.username
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
