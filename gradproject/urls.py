from django.contrib import admin
from django.urls import path, include
from learning import views as learning_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', learning_views.register, name='register'),
    path('student_register/', learning_views.student_register, name='student_register'),
    path('teacher_register/', learning_views.teacher_register, name='teacher_register'),
    path('', learning_views.home, name='home'),
    path('login/', include("django.contrib.auth.urls"), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    path('quiz/', learning_views.quiz, name='quiz'),
    path('pref/', learning_views.poll, name='poll'),
    path('update/', learning_views.update, name='update'),
    path('changepass/', learning_views.change_pass, name='change_pass'),

]
