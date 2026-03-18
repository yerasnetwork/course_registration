from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='teacher_profile', verbose_name="User Account")
    name = models.CharField(max_length=100, verbose_name="ФИО Преподавателя")
    bio = models.TextField(verbose_name="О преподавателе", blank=True)
    expertise = models.CharField(max_length=200, verbose_name="Специализация", blank=True)
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True, verbose_name="Фото")

    # --- ПЕРЕНЕСЛИ ССЫЛКУ СЮДА ---
    linkedin = models.URLField(verbose_name="LinkedIn", blank=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание", blank=True)

    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses', verbose_name="Преподаватель")

    # Отсюда поле teacher_linkedin УБРАЛИ, так как оно теперь у учителя

    max_students = models.PositiveIntegerField(default=30, verbose_name="Максимум мест")
    syllabus = models.FileField(upload_to='syllabuses/', null=True, blank=True, verbose_name="Силабус (PDF/Doc)")

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

# Enrollment и Comment остаются без изменений
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"

    def clean(self):
        if self.course.enrollments.count() >= self.course.max_students:
            raise ValidationError("На курсе закончились места.")

        conflicting_courses = Enrollment.objects.filter(
            student=self.student,
            course__day_of_week=self.course.day_of_week
        ).exclude(course=self.course)

        for enrollment in conflicting_courses:
            existing_course = enrollment.course
            if (self.course.start_time < existing_course.end_time and
                self.course.end_time > existing_course.start_time):
                raise ValidationError(f"Конфликт! Вы уже записаны на {existing_course.title} в это время.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments', verbose_name="Курс")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Студент")
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.course.title}"
class Comment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments', verbose_name="Курс")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Студент")
    text = models.TextField(verbose_name="Текст отзыва")

    # --- НОВОЕ ПОЛЕ: РЕЙТИНГ (1-5) ---
    RATING_CHOICES = (
        (1, '⭐ 1 - Плохо'),
        (2, '⭐⭐ 2 - Так себе'),
        (3, '⭐⭐⭐ 3 - Нормально'),
        (4, '⭐⭐⭐⭐ 4 - Хорошо'),
        (5, '⭐⭐⭐⭐⭐ 5 - Отлично'),
    )
    rating = models.IntegerField(choices=RATING_CHOICES, default=5, verbose_name="Оценка")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.course.title}"

    # Хак для шаблона: возвращает список, чтобы нарисовать звезды циклом
    def get_stars(self):
        return range(self.rating)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")

    def __str__(self):
        return f"Профиль {self.user.username}"
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()