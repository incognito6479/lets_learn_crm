from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Branch, User, Student, Room, Course, Group, Enrollment, Payment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Custom Fields', {'fields': ('role', 'branch', 'created_at')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(Branch)
admin.site.register(Student)
admin.site.register(Room)
admin.site.register(Course)
admin.site.register(Group)
admin.site.register(Enrollment)
admin.site.register(Payment)
