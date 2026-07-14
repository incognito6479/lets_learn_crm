from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend
from .models import Branch, User, Student, Room, Course, Group, Enrollment, Payment, Grade, Absence, Notification, Lead
from .serializers import (
    BranchSerializer, UserSerializer, StudentSerializer, 
    RoomSerializer, CourseSerializer, GroupSerializer, 
    EnrollmentSerializer, PaymentSerializer, GradeSerializer, AbsenceSerializer,
    NotificationSerializer, LeadSerializer
)
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from management.import_excel import run_import_excel
from django.db import transaction
from django.utils import timezone


class ParameterFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        model = queryset.model
        model_fields = set()
        for field in model._meta.get_fields():
            if field.concrete or field.many_to_many:
                model_fields.add(field.name)
                if hasattr(field, 'attname'):
                    model_fields.add(field.attname)

        filter_kwargs = {}
        for param in request.query_params:
            if param in model_fields:
                values = request.query_params.getlist(param)
                if len(values) == 1 and ',' in values[0]:
                    values = [v.strip() for v in values[0].split(',')]

                processed_values = []
                for val in values:
                    if val == '':
                        continue
                    if val.lower() == 'true':
                        processed_values.append(True)
                    elif val.lower() == 'false':
                        processed_values.append(False)
                    elif val.lower() in ('null', 'none'):
                        processed_values.append(None)
                    else:
                        processed_values.append(val)

                if len(processed_values) > 1:
                    filter_kwargs[f"{param}__in"] = processed_values
                elif len(processed_values) == 1:
                    filter_kwargs[param] = processed_values[0]

        return queryset.filter(**filter_kwargs)


class SoftDeleteModelViewSet(viewsets.ModelViewSet):
    filter_backends = [ParameterFilterBackend]
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
    filter_backends = [ParameterFilterBackend]

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
    filter_backends = [ParameterFilterBackend]

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


class LeadViewSet(SoftDeleteModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsCashierOrAdminOrCEOOrSuperuserOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset().exclude(status="converted")
        user = self.request.user
        if user.is_authenticated and user.role == 'admin' and user.branch:
            qs = qs.filter(branch=user.branch)
        
        course_id = self.request.query_params.get('course')
        if course_id:
            qs = qs.filter(course_id=course_id)
            
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
            
        return qs

    @action(detail=False, methods=['post'], url_path='create-group')
    def create_group(self, request):
        name = request.data.get('name')
        teacher_id = request.data.get('teacher')
        room_id = request.data.get('room')
        course_id = request.data.get('course')
        started_at = request.data.get('started_at')
        starts_at = request.data.get('starts_at')
        duration = request.data.get('duration')
        price = request.data.get('price')
        teacher_share = request.data.get('teacher_share', 50)
        group_days_at = request.data.get('group_days_at', 'Mon-Wed-Fri')
        lead_ids = request.data.get('lead_ids', [])

        if not lead_ids:
            raise ValidationError("Please select at least one lead.")
        if not name or not course_id or not started_at or not starts_at or not duration:
            raise ValidationError("Missing required group fields.")
        
        with transaction.atomic():
            leads = Lead.objects.filter(id__in=lead_ids, is_active=True)
            if not leads.exists():
                raise ValidationError("No valid leads found.")
            
            # Inherit branch from first lead
            branch = leads.first().branch
            
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                raise ValidationError("Course not found.")
                
            teacher = User.objects.filter(id=teacher_id, role='teacher').first() if teacher_id else None
            room = Room.objects.filter(id=room_id).first() if room_id else None

            group = Group.objects.create(
                name=name,
                course=course,
                teacher=teacher,
                room=room,
                branch=branch,
                started_at=started_at,
                starts_at=starts_at,
                duration=duration,
                price=price or course.price,
                teacher_share=teacher_share,
                group_days_at=group_days_at,
                status='ongoing'
            )

            for lead in leads:
                student, created = Student.objects.get_or_create(
                    phone1=lead.phone,
                    defaults={
                        'full_name': lead.full_name,
                        'description': lead.notes or f"Converted from lead on {timezone.localdate()}"
                    }
                )
                
                # Enroll student
                Enrollment.objects.get_or_create(
                    student=student,
                    group=group,
                    defaults={
                        'status': 'enrolled'
                    }
                )
                
                # Update lead status to converted
                lead.status = 'converted'
                lead.save()

            return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)
