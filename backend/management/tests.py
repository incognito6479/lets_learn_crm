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

    def test_jwt_obtain_and_refresh_tokens(self):
        user = User.objects.create(
            username="jwtuser",
            role="admin",
            branch=self.branch
        )
        user.set_password("jwtpassword")
        user.save()

        self.client.force_authenticate(user=None)

        # 1. Obtain token pair
        response = self.client.post('/api/token/', {
            'username': 'jwtuser',
            'password': 'jwtpassword'
        }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['username'], 'jwtuser')
        self.assertEqual(response.data['role'], 'admin')

        # 2. Refresh access token
        refresh_token = response.data['refresh']
        response_refresh = self.client.post('/api/token/refresh/', {
            'refresh': refresh_token
        }, format='json')
        self.assertEqual(response_refresh.status_code, 200)
        self.assertIn('access', response_refresh.data)

    def test_teacher_blocked_from_payments(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, 403)

    def test_cashier_blocked_from_grading(self):
        cashier = User.objects.create(
            username="cashier_test",
            role="cashier",
            branch=self.branch
        )
        cashier.set_password("cashierpass")
        cashier.save()
        
        self.client.force_authenticate(user=cashier)
        response = self.client.get('/api/grades/')
        self.assertEqual(response.status_code, 403)

    def test_teacher_share_and_payouts_calculation(self):
        # Create a group specifically for this test
        group = Group.objects.create(
            name="Payout Group",
            course=self.course,
            teacher=self.teacher,
            room=self.room,
            branch=self.branch,
            price=Decimal('100000.00'),
            starts_at='10:00:00',
            duration=90,
            started_at=timezone.localdate(),
            status='ongoing',
            group_days_at='Mon-Wed-Fri',
            teacher_share=40
        )

        # Enroll the student in this group
        Enrollment.objects.create(
            student=self.student,
            group=group,
            status='enrolled'
        )

        Payment.objects.create(
            group=group,
            student=self.student,
            amount=Decimal('100000.00'),
            payment_method='cash',
            status='accepted'
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/groups/{group.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['teacher_earnings'], 40000.00)
        self.assertEqual(response.data['teacher_paid'], 0.00)
        self.assertEqual(response.data['teacher_remaining'], 40000.00)

        Payment.objects.create(
            group=group,
            student=None,
            teacher=self.teacher,
            amount=Decimal('15000.00'),
            payment_method='cash',
            status='accepted'
        )

        response = self.client.get(f'/api/groups/{group.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['teacher_earnings'], 40000.00)
        self.assertEqual(response.data['teacher_paid'], 15000.00)
        self.assertEqual(response.data['teacher_remaining'], 25000.00)

    def test_excel_group_import(self):
        import io
        import openpyxl
        from django.core.files.uploadedfile import SimpleUploadedFile
        from openpyxl.styles import Font

        # Create mock excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Tues 900"

        # Headers
        ws.cell(row=2, column=1, value="№")
        ws.cell(row=2, column=2, value="ФИО")
        ws.cell(row=2, column=3, value="дата оплаты")
        ws.cell(row=2, column=35, value="ИТОГ")
        ws.cell(row=2, column=36, value="примечание")
        ws.cell(row=2, column=37, value="телефон")

        # Row 3: student 1 - Amirshox, date: 24 iyun, total: 450, note: 450 (debt - red text), phone: 93 727 70 07
        ws.cell(row=3, column=1, value=1)
        ws.cell(row=3, column=2, value="Amirshox Davronov")
        ws.cell(row=3, column=3, value="24 iyun")
        ws.cell(row=3, column=4, value="-") # day 1 absence
        ws.cell(row=3, column=35, value=450)
        ws.cell(row=3, column=37, value="93 727 70 07")
        
        red_font = Font(color="FFFF0000")
        ws.cell(row=3, column=36, value=450).font = red_font

        # Row 4: student 2 - Timur, date: 16/Jun, total: 0, note: 450 (overpaid - green text), phone: 88 287 17 72
        ws.cell(row=4, column=1, value=2)
        ws.cell(row=4, column=2, value="Timur Mustafoev")
        ws.cell(row=4, column=3, value="16/Jun")
        ws.cell(row=4, column=35, value=0)
        ws.cell(row=4, column=37, value="88 287 17 72")
        
        green_font = Font(color="FF00FF00")
        ws.cell(row=4, column=36, value=450).font = green_font

        # Row 5: ОБЩИЙ ИТОГ (stops loop)
        ws.cell(row=5, column=2, value="ОБЩИЙ ИТОГ")

        # Save workbook to memory
        excel_buffer = io.BytesIO()
        wb.save(excel_buffer)
        excel_buffer.seek(0)

        uploaded_file = SimpleUploadedFile(
            name="Kadir_K.xlsx",
            content=excel_buffer.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/groups/import-excel/', {
            'file': uploaded_file,
            'month': 7,
            'year': 2026,
            'price': 450000.00
        }, format='multipart')
        self.assertEqual(response.status_code, 200)

        # Check response details
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('Kadir K - Tues 900', response.data['imported_groups'])

        # Verify database objects created
        # 1. Teacher User
        teacher = User.objects.get(username="kadir_k")
        self.assertEqual(teacher.first_name, "Kadir K")
        self.assertEqual(teacher.role, "teacher")

        # 2. Group
        group = Group.objects.get(name="Kadir K - Tues 900")
        self.assertEqual(group.teacher, teacher)
        self.assertEqual(group.group_days_at, "Tue-Thur-Sat")
        self.assertEqual(group.starts_at.hour, 9)

        # 3. Students
        s1 = Student.objects.get(full_name="Amirshox Davronov")
        self.assertEqual(s1.phone1, "+998937277007")

        s2 = Student.objects.get(full_name="Timur Mustafoev")
        self.assertEqual(s2.phone1, "+998882871772")

        # 4. Enrollments
        e1 = Enrollment.objects.get(student=s1, group=group)
        self.assertEqual(e1.date.month, 6)
        self.assertEqual(e1.date.day, 24)

        e2 = Enrollment.objects.get(student=s2, group=group)
        self.assertEqual(e2.date.month, 6)
        self.assertEqual(e2.date.day, 16)

        # 5. Payments
        p1 = Payment.objects.filter(student=s1, group=group, amount=450000.00).count()
        self.assertEqual(p1, 2)

        p2 = Payment.objects.filter(student=s2, group=group, amount=450000.00).count()
        self.assertEqual(p2, 2)

        # 6. Absences
        absences = Absence.objects.filter(student=s1, group=group)
        self.assertEqual(absences.count(), 1)
        self.assertEqual(absences.first().date.day, 1)

    def test_admin_branch_filtering(self):
        # Create Branch B
        branch_b = Branch.objects.create(name="Branch B")

        # Create Admin user linked to Branch A (self.branch)
        admin_a = User.objects.create_user(
            username="admin_a",
            first_name="Admin A",
            password="adminpassword",
            role="admin",
            branch=self.branch
        )

        # Create Group A (Branch A) and Group B (Branch B)
        group_a = Group.objects.create(
            name="Group A",
            starts_at="10:00:00",
            duration=90,
            started_at=timezone.localdate(),
            branch=self.branch,
            status="ongoing"
        )
        group_b = Group.objects.create(
            name="Group B",
            starts_at="10:00:00",
            duration=90,
            started_at=timezone.localdate(),
            branch=branch_b,
            status="ongoing"
        )

        # Create Teachers
        teacher_a = User.objects.create_user(
            username="teacher_a",
            first_name="Teacher A",
            password="pwd",
            role="teacher",
            branch=self.branch
        )
        teacher_b = User.objects.create_user(
            username="teacher_b",
            first_name="Teacher B",
            password="pwd",
            role="teacher",
            branch=branch_b
        )

        # Create Students
        student_a = Student.objects.create(full_name="Student A", phone1="998900000001")
        student_b = Student.objects.create(full_name="Student B", phone1="998900000002")

        # Enrollments
        Enrollment.objects.create(student=student_a, group=group_a)
        Enrollment.objects.create(student=student_b, group=group_b)

        # Payments
        payment_a = Payment.objects.create(
            group=group_a,
            student=student_a,
            amount=Decimal("10000.00"),
            payment_method="cash",
            status="accepted"
        )
        payment_b = Payment.objects.create(
            group=group_b,
            student=student_b,
            amount=Decimal("20000.00"),
            payment_method="cash",
            status="accepted"
        )

        # Authenticate as admin_a (Branch A admin)
        self.client.force_authenticate(user=admin_a)

        # 1. Verify Group filtering
        response = self.client.get('/api/groups/')
        self.assertEqual(response.status_code, 200)
        group_names = [g['name'] for g in response.data]
        self.assertIn("Group A", group_names)
        self.assertNotIn("Group B", group_names)

        # 2. Verify Teacher/User filtering
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 200)
        teacher_names = [u['first_name'] for u in response.data]
        self.assertIn("Teacher A", teacher_names)
        self.assertNotIn("Teacher B", teacher_names)

        # 3. Verify Student filtering
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, 200)
        student_names = [s['full_name'] for s in response.data]
        self.assertIn("Student A", student_names)
        self.assertNotIn("Student B", student_names)

        # 4. Verify Payment filtering
        response = self.client.get('/api/payments/')
        self.assertEqual(response.status_code, 200)
        payment_amounts = [float(p['amount']) for p in response.data]
        self.assertIn(10000.00, payment_amounts)
        self.assertNotIn(20000.00, payment_amounts)
