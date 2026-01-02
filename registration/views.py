from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Enrollment
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegisterForm


def course_list(request):

    courses = Course.objects.all()
    user_enrollments = []
    
    if request.user.is_authenticated:
        user_enrollments = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)

    return render(request, 'registration/course_list.html', {
        'courses': courses,
        'user_enrollments': user_enrollments
    })

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    
    try:
      
        enrollment = Enrollment(student=request.user, course=course)
        enrollment.save()
        messages.success(request, f'Вы успешно записались на курс "{course.title}"!')
        
    except ValidationError as e:
    
        messages.error(request, e.messages[0])

    return redirect('course_list')
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Сразу входим после регистрации
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('course_list')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('course_list')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('course_list')


@login_required
def student_schedule(request):
    # Получаем записи
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    # --- ОТЛАДКА (DEBUG) ---
    print(f"Пользователь: {request.user.username}")
    print(f"Найдено записей: {enrollments.count()}")
    for item in enrollments:
        print(f" - Курс: {item.course.title}")
    # -----------------------

    enrollments = enrollments.order_by('course__day_of_week', 'course__start_time')
    return render(request, 'registration/student_schedule.html', {'enrollments': enrollments})