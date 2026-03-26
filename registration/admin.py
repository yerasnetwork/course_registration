from django.contrib import admin
from .models import Course, Enrollment, Teacher, ParentProfile

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'expertise')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'day_of_week', 'start_time', 'max_students')
    list_filter = ('day_of_week', 'teacher')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_children_count')
    filter_horizontal = ('children',)

    def get_children_count(self, obj):
        return obj.children.count()
    get_children_count.short_description = 'Children'