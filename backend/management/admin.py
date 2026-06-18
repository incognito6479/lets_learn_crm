from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Branch, User, Student, Room, Course, Group, Enrollment, Payment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'branch')}),
    )
    list_display = ('username', 'email', 'role', 'branch', 'is_staff')

admin.site.register(Branch)
admin.site.register(Student)
admin.site.register(Room)
admin.site.register(Course)
admin.site.register(Group)
admin.site.register(Enrollment)
admin.site.register(Payment)
