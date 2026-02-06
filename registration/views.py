import json
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

# Импорт твоих моделей и форм
from .models import Course, Enrollment
from .forms import UserRegisterForm


def course_list(request):
    courses = Course.objects.all()
    user_enrollments = []
    
    # Если пользователь авторизован, получаем список ID курсов, куда он записан
    if request.user.is_authenticated:
        user_enrollments = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)

    return render(request, 'registration/course_list.html', {
        'courses': courses,
        'user_enrollments': user_enrollments
    })

# 2. Детали курса
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'registration/course_detail.html', {'course': course})

# 3. Запись на курс
@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    try:
        enrollment = Enrollment(student=request.user, course=course)
        enrollment.save()  # Тут сработает валидация из models.py
        messages.success(request, f'Вы успешно записались на курс "{course.title}"!')
    except ValidationError as e:
        messages.error(request, e.messages[0])
    return redirect('course_list')

# 4. Мое расписание
@login_required
def student_schedule(request):
    # 1. Получаем все записи студента
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course', 'course__teacher')
    
    # 2. Подготовка структуры данных: Словарь { 'MON': [курс1, курс2], 'TUE': [], ... }
    # Порядок дней важен для отображения
    days_order = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    schedule = {day: [] for day in days_order}
    
    # Раскладываем курсы по дням
    for enrollment in enrollments:
        day = enrollment.course.day_of_week
        if day in schedule:
            schedule[day].append(enrollment.course)

    # Сортируем уроки внутри каждого дня по времени
    for day in schedule:
        schedule[day].sort(key=lambda x: x.start_time)

    # 3. Определяем "Сегодня"
    # datetime.now().weekday() возвращает 0 для Пн, 1 для Вт и т.д.
    weekdays_map = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}
    current_day_code = weekdays_map.get(datetime.now().weekday())

    # Словарь для красивых названий дней на русском
    day_names = {
        'MON': 'Понедельник', 'TUE': 'Вторник', 'WED': 'Среда',
        'THU': 'Четверг', 'FRI': 'Пятница', 'SAT': 'Суббота', 'SUN': 'Воскресенье'
    }

    context = {
        'schedule': schedule,           # Наши уроки по дням
        'current_day_code': current_day_code, # Код сегодняшнего дня (например 'FRI')
        'day_names': day_names,         # Русские названия
    }
    
    return render(request, 'registration/student_schedule.html', context)

# --- АУТЕНТИФИКАЦИЯ ---

# 5. Регистрация
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('course_list')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

# 6. Вход
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

# 7. Выход
def user_logout(request):
    logout(request)
    return redirect('course_list')


# --- API ЭНДПОИНТЫ (Задание №6) ---

@csrf_exempt
def api_courses(request):
    """
    API для получения списка курсов (GET) и создания нового курса (POST).
    """
    if request.method == 'GET':
        courses = list(Course.objects.values(
            'id', 'title', 'description', 'teacher__name', 
            'day_of_week', 'start_time', 'end_time', 'max_students'
        ))
        return JsonResponse(courses, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_course = Course.objects.create(
                title=data.get('title'),
                description=data.get('description', ''),
                day_of_week=data.get('day_of_week', 'MON'),
                start_time=data.get('start_time', '09:00'),
                end_time=data.get('end_time', '10:30'),
                max_students=data.get('max_students', 30)
            )
            return JsonResponse({
                'id': new_course.id, 
                'title': new_course.title,
                'status': 'success'
            }, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


# --- ЧАТ С ИИ (OPENROUTER) ---


@csrf_exempt
def chat_with_gpt(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            # Подготовка контекста
            courses = Course.objects.all()
            course_info = "\n".join([f"- {c.title}: {c.description}" for c in courses])
            system_prompt = f"Ты помощник на сайте курсов. Доступны: {course_info}. Отвечай кратко."

            api_key = ""
            
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://127.0.0.1:8000/", 
                },
                data=json.dumps({
                    "model": "google/gemini-2.0-flash-exp:free",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ]
                }),
                timeout=10 # Добавляем таймаут, чтобы сервер не зависал
            )

            result = response.json()

            # ПРОВЕРКА: есть ли в ответе нужные поля
            if response.status_code == 200 and 'choices' in result:
                reply = result['choices'][0]['message']['content']
                return JsonResponse({'reply': reply})
            else:
                # Если API прислало ошибку, выводим её текст
                error_detail = result.get('error', {}).get('message', 'Модель временно недоступна')
                print(f"!!! API ERROR: {result}")
                return JsonResponse({'reply': f"Извини, возникла ошибка API: {error_detail}"})

        except Exception as e:
            print(f"!!! CRITICAL ERROR: {str(e)}")
            return JsonResponse({'reply': "Проблема на стороне сервера. Попробуй позже."}, status=200) # Ставим 200, чтобы JS не падал

    return JsonResponse({'error': 'Method not allowed'}, status=400)