from django.contrib import admin
from .models import *

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'subject_type')
    list_filter = ('subject_type',)
    search_fields = ('room_number',)

@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ('class_name',)
    search_fields = ('class_name',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'school_class', 'gender', 'classroom')
    list_filter = ('gender', 'school_class', 'classroom')
    search_fields = ('last_name', 'first_name')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_name',)
    search_fields = ('subject_name',)

@admin.register(TeachingPeriod)
class TeachingPeriodAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'school_class', 'start_date', 'end_date')
    list_filter = ('teacher', 'subject', 'school_class')
    search_fields = ('teacher__last_name', 'subject__subject_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'school_class', 'gender')
    list_filter = ('gender', 'school_class')
    search_fields = ('last_name', 'first_name')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'quarter', 'grade', 'date_modified')
    list_filter = ('subject', 'quarter', 'grade')
    search_fields = ('student__last_name', 'subject__subject_name')

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('school_class', 'subject', 'teacher', 'classroom', 'day_of_week', 'lesson_number')
    list_filter = ('school_class', 'day_of_week', 'subject')
    search_fields = ('school_class__class_name', 'subject__subject_name', 'teacher__last_name')