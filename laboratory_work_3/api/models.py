from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Classroom(models.Model):
    """Кабинет"""
    SUBJECT_TYPES = [
        ('basic', 'Базовая дисциплина'),
        ('profile', 'Профильная дисциплина'),
    ]

    room_number = models.CharField(max_length=10, unique=True)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, verbose_name="Тип дисциплины")

    def __str__(self):
        return f"Кабинет {self.room_number} ({self.get_subject_type_display()})"

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"


class SchoolClass(models.Model):
    """Класс"""
    class_name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.class_name

    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"


class Teacher(models.Model):
    """Учитель"""
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]

    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='class_teacher',
        verbose_name="Классное руководство"
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол")
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Закрепленный кабинет"
    )

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    class Meta:
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"


class Subject(models.Model):
    """Предмет"""
    subject_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.subject_name

    class Meta:
        verbose_name = "Предмет"
        verbose_name_plural = "Предметы"


class TeachingPeriod(models.Model):
    """Период преподавания учителем предмета"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teaching_periods')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='teaching_periods')
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='teaching_periods')
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.teacher} - {self.subject} ({self.school_class})"

    class Meta:
        verbose_name = "Период преподавания"
        verbose_name_plural = "Периоды преподавания"


class Student(models.Model):
    """Ученик"""
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]

    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='students')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол")

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.school_class})"

    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"


class Grade(models.Model):
    """Оценка ученика по предмету"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    quarter = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name="Четверть"
    )
    grade = models.IntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        unique_together = ['student', 'subject', 'quarter']

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.quarter} четверть: {self.grade}"


class Schedule(models.Model):
    """Расписание"""
    DAYS_OF_WEEK = [
        (1, 'Понедельник'),
        (2, 'Вторник'),
        (3, 'Среда'),
        (4, 'Четверг'),
        (5, 'Пятница'),
        (6, 'Суббота'),
    ]

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name='schedules')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='schedules')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedules')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    lesson_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписание"
        ordering = ['day_of_week', 'lesson_number']

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.lesson_number} урок: {self.subject} ({self.school_class})"