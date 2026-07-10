from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from django.db.models import Sum
from django.core.validators import MinValueValidator, MaxValueValidator

class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True

class Branch(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class CustomUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
        ('CEO', 'CEO'),
        ('teacher', 'Teacher'),
        ('superuser', 'Superuser'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    email = None
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    objects = CustomUserManager()

    REQUIRED_FIELDS = []

class Student(BaseModel):
    full_name = models.CharField(max_length=255, db_index=True)
    phone1 = models.CharField(max_length=20, db_index=True)
    phone2 = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone1})"

class Room(BaseModel):
    name = models.CharField(max_length=255)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='rooms')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.branch.name})"

class Course(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Group(BaseModel):
    STATUS_CHOICES = (
        ('ongoing', 'Ongoing'),
        ('finished', 'Finished')
    )
    DAYS_CHOICES = (
        ('Mon-Wed-Fri', 'Mon-Wed-Fri'),
        ('Tue-Thur-Sat', 'Tue-Thur-Sat'),
        ('Everyday', 'Everyday')
    )
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, null=True, limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField(Student, through='Enrollment', related_name='groups')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    started_at = models.DateField()
    starts_at = models.TimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled', db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    teacher_share = models.IntegerField(default=50, help_text="Teacher's revenue share percentage")
    group_days_at = models.CharField(max_length=20, choices=DAYS_CHOICES, default='Mon-Wed-Fri')

    def __str__(self):
        return f"{self.name} - {self.teacher} - {self.group_days_at} - {self.starts_at}"

class Enrollment(BaseModel):
    STATUS_CHOICES = (
        ('enrolled', 'Enrolled'),
        ('finished', 'Finished'),
        ('dropped', 'Dropped'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('debt', 'Debt'),
    )
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled', db_index=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='debt', db_index=True)
    debt_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    enrolled_free = models.BooleanField(default=False)
    pdf_uploaded = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'group')
    
    def __str__(self):
        return f"{self.student.full_name} - {self.group.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.debt_amount = 0.00 if self.enrolled_free else self.group.price
            if self.enrolled_free:
                self.payment_status = 'paid'
        super().save(*args, **kwargs)

    def check_debt(self):
        import datetime
        if self.enrolled_free:
            expected_amount = 0
            total_paid = 0
            months_billed = 0
            debt = 0
            new_status = 'paid'
        else:
            today = timezone.localdate()
            start_date = self.date

            if self.pdf_uploaded:
                # Shift start_date to the start of the current billing cycle
                months_elapsed = (today.year - start_date.year) * 12 + (today.month - start_date.month)
                if today.day <= start_date.day:
                    months_elapsed -= 1
                months_elapsed = max(0, months_elapsed)
                
                cy = start_date.year + (start_date.month - 1 + months_elapsed) // 12
                cm = (start_date.month - 1 + months_elapsed) % 12 + 1
                cd = start_date.day
                
                import calendar
                max_days = calendar.monthrange(cy, cm)[1]
                cd = min(cd, max_days)
                start_date = datetime.date(cy, cm, cd)

            if start_date.year > today.year or (start_date.year == today.year and start_date.month > today.month):
                months_billed = 0
            else:
                # 1. Anniversary-based months billed
                months_elapsed = (today.year - start_date.year) * 12 + (today.month - start_date.month)
                if today.day <= start_date.day:
                    months_elapsed -= 1
                anniversary_months_billed = max(0, months_elapsed) + 1

                # 2. Maximum calendar month index containing accepted payments
                payment_qs = Payment.objects.filter(
                    student=self.student,
                    group=self.group,
                    is_active=True,
                    status='accepted'
                )
                if self.pdf_uploaded:
                    start_date_dt = timezone.make_aware(datetime.datetime.combine(start_date, datetime.time.min))
                    payment_qs = payment_qs.filter(payment_date__gte=start_date_dt)
                payment_dates = payment_qs.values_list('payment_date', flat=True)
                
                max_paid_month_index = 0
                for p_date in payment_dates:
                    if p_date:
                        p_local = timezone.localdate(p_date)
                        if p_local <= today:
                            idx_months = (p_local.year - start_date.year) * 12 + (p_local.month - start_date.month)
                            if p_local.day <= start_date.day:
                                idx_months -= 1
                            idx = max(0, idx_months) + 1
                            if idx > max_paid_month_index:
                                max_paid_month_index = idx
                
                # 3. Months billed is the max of anniversary billing and max paid month index
                months_billed = max(anniversary_months_billed, max_paid_month_index)

            group_price = self.group.price
            expected_amount = months_billed * group_price
            
            total_paid_qs = Payment.objects.filter(
                student=self.student,
                group=self.group,
                is_active=True,
                status='accepted'
            )
            today_dt = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))
            total_paid_qs = total_paid_qs.filter(payment_date__lte=today_dt)
            if self.pdf_uploaded:
                start_date_dt = timezone.make_aware(datetime.datetime.combine(start_date, datetime.time.min))
                total_paid_qs = total_paid_qs.filter(payment_date__gte=start_date_dt)
            total_paid = total_paid_qs.aggregate(total=Sum('amount'))['total'] or 0
            debt = expected_amount - total_paid
            if debt < 0:
                debt = 0
            new_status = 'debt' if debt > 0 else 'paid'
        
        changed = False
        if self.payment_status != new_status or self.debt_amount != debt:
            self.payment_status = new_status
            self.debt_amount = debt
            self.save(update_fields=['payment_status', 'debt_amount'])
            changed = True
        return changed, expected_amount, total_paid, months_billed

class Payment(BaseModel):
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('card', 'Card'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending Confirmation'),
        ('accepted', 'Accepted'),
        ('canceled', 'Canceled')
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='accepted', db_index=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, null=True, blank=True)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, limit_choices_to={'role': 'teacher'})
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    payment_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.student:
            enrollment = Enrollment.objects.filter(
                student=self.student,
                group=self.group,
                is_active=True
            ).first()
            if enrollment:
                enrollment.check_debt()

    def __str__(self):
        payer = self.student.full_name if self.student else (f"Teacher: {self.teacher.username}" if self.teacher else "Unknown")
        return f"{payer} - {self.group.name} - {self.amount} - {self.status}"

class Grade(BaseModel):
    enrolled_student = models.ForeignKey(Student, on_delete=models.PROTECT)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={'role': 'teacher'})
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    grade = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    date = models.DateField(default=timezone.localdate)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.enrolled_student.full_name} - {self.group.name} - {self.grade} ({self.date})"

class Absence(BaseModel):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, limit_choices_to={'role': 'teacher'})
    date = models.DateField(default=timezone.localdate)

    def __str__(self):
        return f"{self.student.full_name} - {self.group.name} - {self.date}"

class Notification(BaseModel):
    NOTIFICATION_TYPES = (
        ('absence', 'Absence Alert'),
        ('payment_pending', 'Payment Pending Confirmation'),
        ('payment_accepted', 'Payment Accepted'),
        ('lead_alert', 'Lead Alert'),
    )
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='absence')

    def __str__(self):
        return f"{self.recipient.username} - {self.title} - Read: {self.is_read}"


class Lead(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('coming', 'Coming'),
        ('not_coming', 'Not Coming'),
        ('converted', 'Converted'),
    )
    full_name = models.CharField(max_length=255, db_index=True)
    phone = models.CharField(max_length=20, db_index=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name='leads')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='leads', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.phone}) - {self.course.name}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        old_status = None
        if not is_new:
            try:
                old_status = Lead.objects.get(pk=self.pk).status
            except Lead.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Check threshold if lead became active or is new and active
        status_changed_to_active = (
            is_new and self.is_active and self.status in ['pending', 'coming']
        ) or (
            not is_new and self.is_active and self.status in ['pending', 'coming'] and old_status not in ['pending', 'coming']
        )
        
        if status_changed_to_active:
            count = Lead.objects.filter(
                course=self.course,
                branch=self.branch,
                is_active=True,
                status__in=['pending', 'coming']
            ).count()
            if count > 10:
                admins = User.objects.filter(role='admin', is_active=True)
                for admin in admins:
                    if not admin.branch or admin.branch == self.branch:
                        # Avoid duplicate unread alerts
                        Notification.objects.get_or_create(
                            recipient=admin,
                            title=f"Lead Alert: {self.course.name}",
                            message=f"There are now {count} interested students for course '{self.course.name}' in branch '{self.branch.name}'. Consider creating a new group.",
                            notification_type='lead_alert',
                            is_read=False
                        )

