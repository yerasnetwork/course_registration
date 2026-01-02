from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание", blank=True)
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
        unique_together = ('student', 'course') 

    def clean(self):
        # 1. Проверка лимита мест
        if self.course.enrollments.count() >= self.course.max_students:
            raise ValidationError("На курсе закончились места.")

   
        conflicting_courses = Enrollment.objects.filter(
            student=self.student,
            course__day_of_week=self.course.day_of_week
        ).exclude(course=self.course)

        for enrollment in conflicting_courses:
            existing_course = enrollment.course
            # Если время пересекается
            if (self.course.start_time < existing_course.end_time and
                self.course.end_time > existing_course.start_time):
                raise ValidationError(f"Конфликт времени с курсом: {existing_course.title}")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)