from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate
from management.models import Branch, User, Student, Room, Course, Group, Enrollment, Payment
from management.views import GroupViewSet

class GroupFinishTest(TestCase):
    def setUp(self):
        self.branch = Branch.objects.create(name="Main Branch", description="Main campus center")
        self.teacher = User.objects.create(
            username="teacher1",
            first_name="John",
            last_name="Doe",
            role="teacher"
        )
        self.teacher.set_password("teacherpassword")
        self.teacher.save()
        self.admin = User.objects.create(
            username="admin1",
            first_name="Admin",
            last_name="User",
            role="admin"
        )
        self.admin.set_password("adminpassword")
        self.admin.save()
        self.student = Student.objects.create(
            full_name="Bob Smith",
            phone1="+998904445566"
        )
        self.course = Course.objects.create(
            name="English I",
            price=Decimal('100000.00')
        )
        self.room = Room.objects.create(
            name="Room 1",
            branch=self.branch
        )
        self.group = Group.objects.create(
            name="English Group A",
            course=self.course,
            teacher=self.teacher,
            room=self.room,
            branch=self.branch,
            price=Decimal('100000.00'),
            starts_at="09:00",
            duration=90,
            started_at=timezone.localdate(),
            status="ongoing"
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            group=self.group,
            status="enrolled"
        )
        self.factory = APIRequestFactory()

    def test_finish_group_with_debt_raises_validation_error(self):
        # The student has not paid anything, so they have debt of 100,000 UZS
        self.enrollment.check_debt()
        self.assertEqual(self.enrollment.payment_status, 'debt')

        # Try to patch status to finished
        view = GroupViewSet.as_view({'patch': 'partial_update'})
        request = self.factory.patch(
            f'/api/groups/{self.group.id}/',
            {'status': 'finished'},
            format='json'
        )
        force_authenticate(request, user=self.admin)
        
        response = view(request, pk=self.group.id)
        self.assertEqual(response.status_code, 400)
        self.assertIn("outstanding debt", str(response.data[0]))

        # Assert status remains ongoing
        self.group.refresh_from_db()
        self.assertEqual(self.group.status, 'ongoing')

    def test_finish_group_with_no_debt_succeeds(self):
        # Record payment to clear the debt
        Payment.objects.create(
            student=self.student,
            group=self.group,
            amount=Decimal('100000.00'),
            payment_method="cash",
            status="accepted"
        )
        self.enrollment.check_debt()
        self.assertEqual(self.enrollment.payment_status, 'paid')

        # Try to patch status to finished
        view = GroupViewSet.as_view({'patch': 'partial_update'})
        request = self.factory.patch(
            f'/api/groups/{self.group.id}/',
            {'status': 'finished'},
            format='json'
        )
        force_authenticate(request, user=self.admin)
        
        response = view(request, pk=self.group.id)
        self.assertEqual(response.status_code, 200)

        # Assert status is updated to finished
        self.group.refresh_from_db()
        self.assertEqual(self.group.status, 'finished')

        # Assert enrollment status is updated to finished
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, 'finished')
