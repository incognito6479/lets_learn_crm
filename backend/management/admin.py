from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Branch, User, Student, Room, Course, Group, Enrollment, Payment, Grade, Absence, Notification, Lead

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Custom Fields', {'fields': ('role', 'branch', 'created_at')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'title', 'message')

admin.site.register(Branch)
admin.site.register(Student)
admin.site.register(Room)
admin.site.register(Course)
admin.site.register(Group)
admin.site.register(Enrollment)
admin.site.register(Payment)
admin.site.register(Grade)
admin.site.register(Absence)
admin.site.register(Lead)
