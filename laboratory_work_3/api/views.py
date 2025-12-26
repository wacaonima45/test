from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from django.http import HttpResponse
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO

from .models import *
from .serializers import *
from .permissions import IsDeputyDirector
from .filters import *


class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
    permission_classes = [IsAuthenticated, IsDeputyDirector]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ClassroomFilter


class SchoolClassViewSet(viewsets.ModelViewSet):
    queryset = SchoolClass.objects.all().annotate(
        students_count=Count('students')
    )
    serializer_class = SchoolClassSerializer
    permission_classes = [IsAuthenticated, IsDeputyDirector]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SchoolClassFilter


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all().prefetch_related('teaching_periods__subject')
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, IsDeputyDirector]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TeacherFilter

    @action(detail=True, methods=['get'])
    def same_subject_teachers(self, request, pk=None):
        """Список учителей, преподающих те же предметы, что и учитель, ведущий информатику в заданном классе"""
        try:
            teacher = self.get_object()
            # Получаем предметы, которые преподает данный учитель
            teacher_subjects = Subject.objects.filter(
                teaching_periods__teacher=teacher
            ).distinct()

            # Находим учителей информатики
            informatics = Subject.objects.filter(subject_name__icontains='информатик').first()

            if not informatics:
                return Response({"error": "Предмет 'Информатика' не найден"},
                                status=status.HTTP_404_NOT_FOUND)

            # Находим учителей, преподающих те же предметы
            same_subject_teachers = Teacher.objects.filter(
                teaching_periods__subject__in=teacher_subjects
            ).distinct().exclude(id=teacher.id)

            serializer = self.get_serializer(same_subject_teachers, many=True)
            return Response(serializer.data)
        except Teacher.DoesNotExist:
            return Response({"error": "Учитель не найден"},
                            status=status.HTTP_404_NOT_FOUND)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all().annotate(
        teachers_count=Count('teaching_periods__teacher', distinct=True)
    )
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated, IsDeputyDirector]
    filter_backends = [DjangoFilterBackend]
    filterset_class = SubjectFilter

    @action(detail=False, methods=['get'])
    def teachers_count(self, request):
        """Сколько учителей преподает каждую из дисциплин в школе"""
        subjects = self.get_queryset()
        data = []
        for subject in subjects:
            teachers_count = Teacher.objects.filter(
                teaching_periods__subject=subject
            ).distinct().count()
            data.append({
                'subject': subject.subject_name,
                'teachers_count': teachers_count
            })
        return Response(data)


class TeachingPeriodViewSet(viewsets.ModelViewSet):
    queryset = TeachingPeriod.objects.all().select_related('teacher', 'subject', 'school_class')
    serializer_class = TeachingPeriodSerializer
    permission_classes = [IsAuthenticated, IsDeputyDirector]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TeachingPeriodFilter


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all().select_related('school_class')
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, IsDeputyDirector]
    filter_backends = [DjangoFilterBackend]
    filterset_class = StudentFilter


class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all().select_related('student', 'subject')
    serializer_class = GradeSerializer
    permission_classes = [IsAuthenticated, IsDeputyDirector]
    filter_backends = [DjangoFilterBackend]
    filterset_class = GradeFilter


class ScheduleViewSet(viewsets.ModelViewSet):
    queryset = Schedule.objects.all().select_related(
        'school_class', 'subject', 'teacher', 'classroom'
    )
    serializer_class = ScheduleSerializer
    permission_classes = [IsAuthenticated, IsDeputyDirector]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ScheduleFilter

    @action(detail=False, methods=['get'])
    def get_lesson(self, request):
        """Какой предмет будет в заданном классе, в заданный день недели на заданном уроке?"""
        class_id = request.query_params.get('class_id')
        day_of_week = request.query_params.get('day_of_week')
        lesson_number = request.query_params.get('lesson_number')

        if not all([class_id, day_of_week, lesson_number]):
            return Response(
                {"error": "Необходимо указать class_id, day_of_week и lesson_number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            schedule = Schedule.objects.get(
                school_class_id=class_id,
                day_of_week=day_of_week,
                lesson_number=lesson_number
            )
            serializer = self.get_serializer(schedule)
            return Response(serializer.data)
        except Schedule.DoesNotExist:
            return Response(
                {"message": "Урок не найден"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Schedule.MultipleObjectsReturned:
            schedules = Schedule.objects.filter(
                school_class_id=class_id,
                day_of_week=day_of_week,
                lesson_number=lesson_number
            )
            serializer = self.get_serializer(schedules, many=True)
            return Response(serializer.data)


class ReportView(generics.GenericAPIView):
    """Генерация отчетов"""
    permission_classes = [IsAuthenticated, IsDeputyDirector]

    def get(self, request, *args, **kwargs):
        report_type = request.query_params.get('type')
        class_id = request.query_params.get('class_id')

        if report_type == 'class_performance':
            return self.generate_class_performance_report(class_id)
        elif report_type == 'gender_statistics':
            return self.generate_gender_statistics()
        elif report_type == 'classroom_statistics':
            return self.generate_classroom_statistics()
        else:
            return Response(
                {"error": "Неверный тип отчета. Доступные: class_performance, gender_statistics, classroom_statistics"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def generate_class_performance_report(self, class_id):
        """Отчет об успеваемости заданного класса"""
        if not class_id:
            return Response(
                {"error": "Необходимо указать class_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            school_class = SchoolClass.objects.get(id=class_id)
            students = Student.objects.filter(school_class=school_class)

            # Получаем классного руководителя
            class_teacher = Teacher.objects.filter(school_class=school_class).first()

            # Получаем все предметы, которые есть у учеников класса
            subjects = Subject.objects.filter(
                grades__student__in=students
            ).distinct()

            subjects_data = {}
            class_total_sum = 0
            class_total_count = 0

            for subject in subjects:
                grades = Grade.objects.filter(
                    student__in=students,
                    subject=subject
                )

                if grades.exists():
                    avg_grade = grades.aggregate(avg=Avg('grade'))['avg']
                    grades_count = grades.count()

                    subjects_data[subject.subject_name] = {
                        'average_grade': round(avg_grade, 2),
                        'grades_count': grades_count
                    }

                    class_total_sum += avg_grade * grades_count
                    class_total_count += grades_count

            class_average = round(class_total_sum / class_total_count, 2) if class_total_count > 0 else 0

            report_data = {
                'class_name': school_class.class_name,
                'class_teacher': f"{class_teacher.last_name} {class_teacher.first_name}" if class_teacher else "Не назначен",
                'total_students': students.count(),
                'subjects_data': subjects_data,
                'class_average': class_average
            }

            # Формат ответа (JSON или PDF)
            format_type = self.request.query_params.get('format', 'json')

            if format_type == 'pdf':
                return self.generate_pdf_report(report_data)
            else:
                return Response(report_data)

        except SchoolClass.DoesNotExist:
            return Response(
                {"error": "Класс не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

    def generate_gender_statistics(self):
        """Сколько мальчиков и девочек в каждом классе?"""
        classes = SchoolClass.objects.all()
        statistics = []

        for school_class in classes:
            boys_count = Student.objects.filter(
                school_class=school_class,
                gender='M'
            ).count()

            girls_count = Student.objects.filter(
                school_class=school_class,
                gender='F'
            ).count()

            statistics.append({
                'class_name': school_class.class_name,
                'boys_count': boys_count,
                'girls_count': girls_count,
                'total_students': boys_count + girls_count
            })

        return Response(statistics)

    def generate_classroom_statistics(self):
        """Сколько кабинетов в школе для базовых и профильных дисциплин?"""
        basic_count = Classroom.objects.filter(subject_type='basic').count()
        profile_count = Classroom.objects.filter(subject_type='profile').count()

        statistics = [
            {
                'subject_type': 'basic',
                'subject_type_display': 'Базовая дисциплина',
                'classroom_count': basic_count
            },
            {
                'subject_type': 'profile',
                'subject_type_display': 'Профильная дисциплина',
                'classroom_count': profile_count
            }
        ]

        return Response(statistics)

    def generate_pdf_report(self, report_data):
        """Генерация PDF отчета"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()

        # Заголовок
        title = Paragraph(f"Отчет об успеваемости класса {report_data['class_name']}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Информация о классе
        class_info = [
            f"Классный руководитель: {report_data['class_teacher']}",
            f"Количество учеников: {report_data['total_students']}",
            f"Средний балл по классу: {report_data['class_average']}"
        ]

        for info in class_info:
            elements.append(Paragraph(info, styles['Normal']))

        elements.append(Spacer(1, 24))

        # Таблица с предметами
        if report_data['subjects_data']:
            table_data = [['Предмет', 'Средний балл', 'Количество оценок']]

            for subject, data in report_data['subjects_data'].items():
                table_data.append([
                    subject,
                    str(data['average_grade']),
                    str(data['grades_count'])
                ])

            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            elements.append(table)

        doc.build(elements)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="class_report_{report_data["class_name"]}.pdf"'

        return response