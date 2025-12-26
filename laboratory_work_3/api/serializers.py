from rest_framework import serializers
from .models import *
from django.db.models import Avg, Count


class ClassroomSerializer(serializers.ModelSerializer):
    subject_type_display = serializers.CharField(source='get_subject_type_display', read_only=True)

    class Meta:
        model = Classroom
        fields = '__all__'


class SchoolClassSerializer(serializers.ModelSerializer):
    class_teacher_name = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = SchoolClass
        fields = '__all__'

    def get_class_teacher_name(self, obj):
        teacher = obj.class_teacher.first()
        return f"{teacher.last_name} {teacher.first_name}" if teacher else None

    def get_students_count(self, obj):
        return obj.students.count()


class TeacherSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    classroom_number = serializers.CharField(source='classroom.room_number', read_only=True)
    subjects = serializers.SerializerMethodField()
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)

    class Meta:
        model = Teacher
        fields = '__all__'

    def get_subjects(self, obj):
        subjects = Subject.objects.filter(
            teaching_periods__teacher=obj
        ).distinct().values_list('subject_name', flat=True)
        return list(subjects)


class SubjectSerializer(serializers.ModelSerializer):
    teachers_count = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = '__all__'

    def get_teachers_count(self, obj):
        return Teacher.objects.filter(teaching_periods__subject=obj).distinct().count()


class TeachingPeriodSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.__str__', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)

    class Meta:
        model = TeachingPeriod
        fields = '__all__'


class StudentSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)

    class Meta:
        model = Student
        fields = '__all__'


class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.__str__', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)

    class Meta:
        model = Grade
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    teacher_name = serializers.CharField(source='teacher.__str__', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    classroom_number = serializers.CharField(source='classroom.room_number', read_only=True)
    class_name = serializers.CharField(source='school_class.class_name', read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'


class ClassReportSerializer(serializers.Serializer):
    """Сериализатор для отчета об успеваемости класса"""
    class_name = serializers.CharField()
    class_teacher = serializers.CharField()
    total_students = serializers.IntegerField()
    subjects_data = serializers.DictField(
        child=serializers.DictField(
            child=serializers.FloatField()
        )
    )
    class_average = serializers.FloatField()


class GenderStatisticsSerializer(serializers.Serializer):
    """Сериализатор для статистики по полу в классах"""
    class_name = serializers.CharField()
    boys_count = serializers.IntegerField()
    girls_count = serializers.IntegerField()
    total_students = serializers.IntegerField()


class ClassroomStatisticsSerializer(serializers.Serializer):
    """Сериализатор для статистики по кабинетам"""
    subject_type = serializers.CharField()
    subject_type_display = serializers.CharField()
    classroom_count = serializers.IntegerField()