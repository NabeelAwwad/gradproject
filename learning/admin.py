from django.contrib import admin
from .models import Material, Student, User, Question, Poll, Topic, Score
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.models import LogEntry

# LogEntry.objects.all().delete()
admin.site.register(Material)
admin.site.register(Student)
admin.site.register(User, UserAdmin)
admin.site.register(Question)
admin.site.register(Poll)
admin.site.register(Topic)
admin.site.register(Score)
