from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from .models import Branch, User, Student, Room, Course, Group, Enrollment, Payment, Grade, Absence, Notification
from .serializers import (
    BranchSerializer, UserSerializer, StudentSerializer, 
    RoomSerializer, CourseSerializer, GroupSerializer, 
    EnrollmentSerializer, PaymentSerializer, GradeSerializer, AbsenceSerializer,
    NotificationSerializer
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from management.import_excel import run_import_excel

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
        qs = self.queryset.all()
        user = self.request.user
        if user.is_authenticated and user.role == 'admin' and user.branch:
            qs = qs.filter(Q(branch=user.branch) | Q(branch__isnull=True) | Q(group__branch=user.branch)).distinct()
        return qs

    @action(detail=True, methods=['get'], url_path='payments')
    def get_payments(self, request, pk=None):
        teacher = self.get_object()
        payments = Payment.objects.filter(teacher=teacher, student__isnull=True, is_active=True)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

class StudentViewSet(SoftDeleteModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsCashierOrAdminOrCEOOrSuperuserOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.role == 'admin' and user.branch:
            qs = qs.filter(
                Q(enrollment__group__branch=user.branch) | 
                Q(enrollment__isnull=True) | 
                Q(enrollment__group__branch__isnull=True)
            ).distinct()
        return qs

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

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.role == 'admin' and user.branch:
            qs = qs.filter(Q(branch=user.branch) | Q(branch__isnull=True))
        return qs

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

    @action(detail=False, methods=['post'], url_path='import-excel')
    def import_excel(self, request):
        excel_file = request.FILES.get('file')
        if not excel_file:
            raise ValidationError("No file was uploaded.")
        month = request.data.get('month')
        year = request.data.get('year')
        price = request.data.get('price')
        result = run_import_excel(excel_file, month, year, price)
        return Response(result)

class EnrollmentViewSet(SoftDeleteModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsCashierOrAdminOrCEOOrSuperuserOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.role == 'admin' and user.branch:
            qs = qs.filter(Q(group__branch=user.branch) | Q(group__branch__isnull=True))
        return qs

    def perform_destroy(self, instance):
        instance.status = 'dropped'
        instance.save()

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsCashierOrAdminOrCEOOrSuperuser]

    def get_permissions(self):
        if self.action == 'confirm_payment':
            return [permissions.IsAuthenticated()]
        return [IsCashierOrAdminOrCEOOrSuperuser()]

    def get_queryset(self):
        qs = self.queryset.all()
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'admin' and user.branch:
                qs = qs.filter(Q(group__branch=user.branch) | Q(group__branch__isnull=True))
            elif user.role == 'teacher':
                qs = qs.filter(teacher=user)
        return qs

    def perform_create(self, serializer):
        is_payout = serializer.validated_data.get('student') is None and serializer.validated_data.get('teacher') is not None
        status = 'pending' if is_payout else 'accepted'
        
        payment = serializer.save(status=status)
        if payment.student:
            enrollment = Enrollment.objects.filter(
                student=payment.student,
                group=payment.group,
                is_active=True
            ).first()
            if enrollment:
                enrollment.check_debt()
        elif is_payout:
            Notification.objects.create(
                recipient=payment.teacher,
                title=f"Payout Pending Confirmation #{payment.id}",
                message=f"Admin registered a payout of {payment.amount} UZS for group {payment.group.name}. Please confirm receipt.",
                notification_type='payment_pending'
            )

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.status = 'canceled'
        instance.save()

    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm_payment(self, request, pk=None):
        payment = self.get_object()
        if request.user.role != 'teacher' or payment.teacher != request.user:
            return Response({'error': 'You are not authorized to confirm this payment.'}, status=status.HTTP_403_FORBIDDEN)
        if payment.status != 'pending':
            return Response({'error': 'This payment is not pending confirmation.'}, status=status.HTTP_400_BAD_REQUEST)
        
        payment.status = 'accepted'
        payment.save()
        
        # Update teacher's pending notification title at the backend
        Notification.objects.filter(
            recipient=payment.teacher,
            notification_type='payment_pending',
            title=f"Payout Pending Confirmation #{payment.id}"
        ).update(
            title=f"Payout Confirmed #{payment.id}"
        )
        
        # Notify admins
        admins = User.objects.filter(role='admin')
        for admin in admins:
            if not admin.branch or admin.branch == payment.group.branch:
                Notification.objects.create(
                    recipient=admin,
                    title="Payout Confirmed",
                    message=f"Teacher {payment.teacher.first_name or payment.teacher.username} confirmed receipt of {payment.amount} UZS for group {payment.group.name}.",
                    notification_type='payment_accepted'
                )
        return Response({'status': 'Payment confirmed successfully.'})

class GradeViewSet(SoftDeleteModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsTeacherOrAdminOrCEOOrSuperuser]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.role == 'admin' and user.branch:
            qs = qs.filter(Q(group__branch=user.branch) | Q(group__branch__isnull=True))
        return qs

class AbsenceViewSet(SoftDeleteModelViewSet):
    queryset = Absence.objects.all()
    serializer_class = AbsenceSerializer
    permission_classes = [IsTeacherOrAdminOrCEOOrSuperuser]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.role == 'admin' and user.branch:
            qs = qs.filter(Q(group__branch=user.branch) | Q(group__branch__isnull=True))
        return qs

    def perform_create(self, serializer):
        absence = serializer.save()
        # Find and notify admins
        admins = User.objects.filter(role='admin')
        for admin in admins:
            if not admin.branch or admin.branch == absence.group.branch:
                Notification.objects.create(
                    recipient=admin,
                    title="Student Absence Alert",
                    message=f"Student {absence.student.full_name} was marked absent in group {absence.group.name} by teacher {absence.teacher.first_name or absence.teacher.username}.",
                    notification_type='absence'
                )

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        recipient_id = self.request.query_params.get('recipient')
        if recipient_id and (user.role in ['admin', 'ceo'] or user.is_superuser):
            return self.queryset.filter(recipient_id=recipient_id, is_active=True).order_by('-created_at')
        return self.queryset.filter(recipient=user, is_active=True).order_by('-created_at')

    @action(detail=True, methods=['post'], url_path='read')
    def mark_as_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'Notification marked as read.'})

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})

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
