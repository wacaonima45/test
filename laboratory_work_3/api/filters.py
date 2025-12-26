import django_filters
from .models import *


class ClassroomFilter(django_filters.FilterSet):
    subject_type = django_filters.ChoiceFilter(choices=Classroom.SUBJECT_TYPES)
    room_number = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Classroom
        fields = ['room_number', 'subject_type']


class SchoolClassFilter(django_filters.FilterSet):
    class_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = SchoolClass
        fields = ['class_name']


class TeacherFilter(django_filters.FilterSet):
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    gender = django_filters.ChoiceFilter(choices=Teacher.GENDER_CHOICES)
    has_classroom = django_filters.BooleanFilter(method='filter_has_classroom')

    class Meta:
        model = Teacher
        fields = ['last_name', 'first_name', 'gender', 'school_class', 'classroom']

    def filter_has_classroom(self, queryset, name, value):
        if value:
            return queryset.filter(classroom__isnull=False)
        return queryset.filter(classroom__isnull=True)


class SubjectFilter(django_filters.FilterSet):
    subject_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Subject
        fields = ['subject_name']


class TeachingPeriodFilter(django_filters.FilterSet):
    class Meta:
        model = TeachingPeriod
        fields = ['teacher', 'subject', 'school_class']


class StudentFilter(django_filters.FilterSet):
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    gender = django_filters.ChoiceFilter(choices=Student.GENDER_CHOICES)

    class Meta:
        model = Student
        fields = ['last_name', 'first_name', 'gender', 'school_class']


class GradeFilter(django_filters.FilterSet):
    student = django_filters.ModelChoiceFilter(queryset=Student.objects.all())
    subject = django_filters.ModelChoiceFilter(queryset=Subject.objects.all())
    quarter = django_filters.NumberFilter()
    grade = django_filters.NumberFilter()

    class Meta:
        model = Grade
        fields = ['student', 'subject', 'quarter', 'grade']


class ScheduleFilter(django_filters.FilterSet):
    school_class = django_filters.ModelChoiceFilter(queryset=SchoolClass.objects.all())
    day_of_week = django_filters.NumberFilter()
    lesson_number = django_filters.NumberFilter()

    class Meta:
        model = Schedule
        fields = ['school_class', 'day_of_week', 'lesson_number', 'subject', 'teacher']