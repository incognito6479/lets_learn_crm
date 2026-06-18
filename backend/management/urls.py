from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BranchViewSet, UserViewSet, StudentViewSet, 
    RoomViewSet, CourseViewSet, GroupViewSet, 
    EnrollmentViewSet, PaymentViewSet
)

router = DefaultRouter()
router.register(r'branches', BranchViewSet)
router.register(r'users', UserViewSet)
router.register(r'students', StudentViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
