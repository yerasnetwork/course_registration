from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('my-schedule/', views.student_schedule, name='student_schedule'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('api/courses/', views.api_courses, name='api_courses'),
    path('api/chat/', views.chat_with_gpt, name='api_chat'),

]