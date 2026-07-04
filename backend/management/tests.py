from django.test import TestCase
from decimal import Decimal
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase
from management.models import Branch, User, Student, Room, Course, Group, Enrollment, Payment, Grade, Absence
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


class APIOperationsTest(APITestCase):
    def setUp(self):
        # Create default records for relations
        self.branch = Branch.objects.create(name="Test Branch", description="Test Branch Description")
        self.admin = User.objects.create_superuser(
            username="superuser",
            password="superpassword",
            role="superuser",
            branch=self.branch
        )
        self.teacher = User.objects.create(
            username="teacher_test",
            role="teacher",
            branch=self.branch
        )
        self.teacher.set_password("teacherpass")
        self.teacher.save()
        
        self.course = Course.objects.create(name="Maths", price=Decimal('150000.00'))
        self.room = Room.objects.create(name="Room 101", branch=self.branch)
        self.student = Student.objects.create(full_name="Alice Johnson", phone1="+998901112233")
        
        # Authenticate all API client calls by default with the superuser
        self.client.force_authenticate(user=self.admin)

    def test_create_group(self):
        response = self.client.post('/api/groups/', {
            'name': 'New Group',
            'course': self.course.id,
            'teacher': self.teacher.id,
            'room': self.room.id,
            'branch': self.branch.id,
            'price': '120000.00',
            'starts_at': '10:00:00',
            'duration': 90,
            'started_at': str(timezone.localdate()),
            'status': 'ongoing',
            'group_days_at': 'Mon-Wed-Fri'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Group.objects.filter(name='New Group').count(), 1)

    def test_create_user(self):
        response = self.client.post('/api/users/', {
            'username': 'newuser',
            'password': 'newpassword',
            'role': 'cashier',
            'branch': self.branch.id,
            'first_name': 'New',
            'last_name': 'User'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username='newuser')
        self.assertEqual(user.role, 'cashier')
        self.assertTrue(user.check_password('newpassword'))

    def test_change_password(self):
        # Change password of the teacher user
        response = self.client.patch(f'/api/users/{self.teacher.id}/', {
            'password': 'changedpassword'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.teacher.refresh_from_db()
        self.assertTrue(self.teacher.check_password('changedpassword'))

    def test_enroll_student(self):
        # Create group for enrollment
        group = Group.objects.create(
            name="Enrollment Test Group",
            course=self.course,
            teacher=self.teacher,
            room=self.room,
            branch=self.branch,
            price=Decimal('150000.00'),
            starts_at="10:00",
            duration=90,
            started_at=timezone.localdate()
        )
        response = self.client.post('/api/enrollments/', {
            'student': self.student.id,
            'group': group.id,
            'status': 'enrolled',
            'payment_status': 'debt'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Enrollment.objects.filter(student=self.student, group=group).count(), 1)

    def test_exclude_student(self):
        # Exclude means soft deleting / marking enrollment as dropped
        group = Group.objects.create(
            name="Exclude Test Group",
            course=self.course,
            teacher=self.teacher,
            room=self.room,
            branch=self.branch,
            price=Decimal('150000.00'),
            starts_at="10:00",
            duration=90,
            started_at=timezone.localdate()
        )
        enrollment = Enrollment.objects.create(
            student=self.student,
            group=group,
            status='enrolled'
        )
        response = self.client.delete(f'/api/enrollments/{enrollment.id}/')
        self.assertEqual(response.status_code, 204) # Soft delete returns 204
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, 'dropped')

    def test_make_payment(self):
        group = Group.objects.create(
            name="Payment Test Group",
            course=self.course,
            teacher=self.teacher,
            room=self.room,
            branch=self.branch,
            price=Decimal('150000.00'),
            starts_at="10:00",
            duration=90,
            started_at=timezone.localdate()
        )
        enrollment = Enrollment.objects.create(
            student=self.student,
            group=group,
            status='enrolled'
        )
        response = self.client.post('/api/payments/', {
            'student': self.student.id,
            'group': group.id,
            'amount': '150000.00',
            'payment_method': 'card',
            'status': 'accepted',
            'description': 'Test payment'
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Payment.objects.filter(student=self.student, group=group).count(), 1)
        
        # Payment trigger perform_create calls check_debt, clearing the debt
        enrollment.refresh_from_db()
        self.assertEqual(enrollment.payment_status, 'paid')
        self.assertEqual(float(enrollment.debt_amount), 0.0)

    def test_grading(self):
        group = Group.objects.create(
            name="Grading Test Group",
            course=self.course,
            teacher=self.teacher,
            room=self.room,
            branch=self.branch,
            price=Decimal('150000.00'),
            starts_at="10:00",
            duration=90,
            started_at=timezone.localdate()
        )
        enrollment = Enrollment.objects.create(
            student=self.student,
            group=group,
            status='enrolled'
        )
        response = self.client.post('/api/grades/', {
            'enrolled_student': self.student.id,
            'group': group.id,
            'teacher': self.teacher.id,
            'grade': 5,
            'date': str(timezone.localdate())
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Grade.objects.filter(enrolled_student=self.student, group=group).count(), 1)

    def test_make_absence(self):
        group = Group.objects.create(
            name="Absence Test Group",
            course=self.course,
            teacher=self.teacher,
            room=self.room,
            branch=self.branch,
            price=Decimal('150000.00'),
            starts_at="10:00",
            duration=90,
            started_at=timezone.localdate()
        )
        enrollment = Enrollment.objects.create(
            student=self.student,
            group=group,
            status='enrolled'
        )
        response = self.client.post('/api/absences/', {
            'student': self.student.id,
            'group': group.id,
            'teacher': self.teacher.id,
            'date': str(timezone.localdate())
        }, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Absence.objects.filter(student=self.student, group=group).count(), 1)
