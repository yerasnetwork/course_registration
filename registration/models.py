from tkinter import image_names
from django.core.files import uploadhandler
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Teacher(models.Model):
    name = models.CharField(max_length=100, verbose_name="ФИО Преподавателя")
    bio = models.TextField(verbose_name="О преподавателе", blank=True)
    expertise = models.CharField(max_length=200, verbose_name="Специализация", blank=True)
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True, verbose_name="Фото")

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание (для чего, для кого)", blank=True)
    
    # Ссылка на учителя 
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses', verbose_name="Преподаватель")
    
    # Линк на LinkedIn и прочее 
    teacher_linkedin = models.URLField(verbose_name="LinkedIn преподавателя", blank=True)
    
    max_students = models.PositiveIntegerField(default=30, verbose_name="Максимум мест")
    
    DAYS_OF_WEEK = (
        ('MON', 'Понедельник'),
        ('TUE', 'Вторник'),
        ('WED', 'Среда'),
        ('THU', 'Четверг'),
        ('FRI', 'Пятница'),
    )
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK, verbose_name="День недели")
    start_time = models.TimeField(verbose_name="Начало")
    end_time = models.TimeField(verbose_name="Конец")

    def __str__(self):
        return f"{self.title} ({self.get_day_of_week_display()})"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course') # Один студент не может записаться дважды на один курс

    def clean(self):
        # 1. Проверка лимита мест
        if self.course.enrollments.count() >= self.course.max_students:
            raise ValidationError("На курсе закончились места.")

        # 2. Проверка пересечения времени
        conflicting_courses = Enrollment.objects.filter(
            student=self.student,
            course__day_of_week=self.course.day_of_week
        ).exclude(course=self.course)

        for enrollment in conflicting_courses:
            existing_course = enrollment.course
            # Проверка пересечения интервалов
            if (self.course.start_time < existing_course.end_time and
                self.course.end_time > existing_course.start_time):
                raise ValidationError(f"Конфликт! Вы уже записаны на {existing_course.title} в это время.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)