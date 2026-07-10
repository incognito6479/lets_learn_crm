from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BranchViewSet, UserViewSet, StudentViewSet, 
    RoomViewSet, CourseViewSet, GroupViewSet, 
    EnrollmentViewSet, PaymentViewSet, GradeViewSet, AbsenceViewSet,
    CustomTokenObtainPairView, NotificationViewSet, LeadViewSet
)
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'branches', BranchViewSet)
router.register(r'users', UserViewSet)
router.register(r'students', StudentViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'courses', CourseViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'grades', GradeViewSet)
router.register(r'absences', AbsenceViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'leads', LeadViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
