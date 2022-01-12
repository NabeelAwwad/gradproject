from django.contrib import admin
from .models import Material, Student, User, Question, Poll, Level, Score
from django.contrib.auth.admin import UserAdmin

admin.site.register(Material)
admin.site.register(Student)
admin.site.register(User, UserAdmin)
admin.site.register(Question)
admin.site.register(Poll)
admin.site.register(Level)
admin.site.register(Score)
