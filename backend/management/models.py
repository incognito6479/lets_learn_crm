from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class BaseModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class Branch(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

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

    REQUIRED_FIELDS = []

class Student(BaseModel):
    full_name = models.CharField(max_length=255)
    phone1 = models.CharField(max_length=20)
    phone2 = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.full_name

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
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(User, on_delete=models.PROTECT, null=True, limit_choices_to={'role': 'teacher'})
    students = models.ManyToManyField(Student, through='Enrollment', related_name='groups')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, null=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT)
    started_at = models.DateField()
    starts_at = models.TimeField()
    duration = models.IntegerField(help_text="Duration in minutes")
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='enrolled')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='debt')
    debt_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('student', 'group')
    
    def __str__(self):
        return f"{self.student.full_name} - {self.group.name}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.debt_amount = self.group.price
        super().save(*args, **kwargs)

    def check_debt(self):
        from django.db.models import Sum
        from django.utils import timezone
        
        today = timezone.localdate()
        start_date = self.date
        
        if start_date > today:
            months_billed = 0
        else:
            months_elapsed = (today.year - start_date.year) * 12 + (today.month - start_date.month)
            if today.day < start_date.day:
                months_elapsed -= 1
            months_billed = max(0, months_elapsed) + 1

        group_price = self.group.price
        expected_amount = months_billed * group_price

        from .models import Payment
        total_paid = Payment.objects.filter(
            student=self.student,
            group=self.group,
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or 0

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
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    payment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.full_name} - {self.group.name} - {self.amount}"
