from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'classrooms', views.ClassroomViewSet)
router.register(r'school-classes', views.SchoolClassViewSet)
router.register(r'teachers', views.TeacherViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'teaching-periods', views.TeachingPeriodViewSet)
router.register(r'students', views.StudentViewSet)
router.register(r'grades', views.GradeViewSet)
router.register(r'schedules', views.ScheduleViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('reports/', views.ReportView.as_view(), name='reports'),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]