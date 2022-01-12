from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)


# class Teacher(models.Model):
#    user = models.OneToOneField(User, on_delete=models.CASCADE)

PREFERENCE_TYPES = (
    ('V', 'Visual'),
    ('A', 'Auditory '),
    ('R', 'Read/Write'),
    ('K', 'Kinesthetic'),
    ('VA', 'Multimodal VA'),
    ('VR', 'Multimodal VR'),
    ('VK', 'Multimodal VK'),
    ('AR', 'Multimodal AR'),
    ('AK', 'Multimodal AK'),
    ('RK', 'Multimodal RK'),
    ('VAR', 'Multimodal VAR'),
    ('VAK', 'Multimodal VAK'),
    ('VRK', 'Multimodal VRK'),
    ('ARK', 'Multimodal ARK'),
    ('VARK', 'Multimodal VARK'),
)

MATERIAL_TYPES = (
    ('V', 'Visual'),
    ('A', 'Auditory '),
    ('R', 'Read/Write'),
    ('K', 'Kinesthetic'),
)

MATERIAL_LENGTH = (
    ('S', 'Short'),
    ('L', 'Long')
)

class Level(models.Model):
    name = models.CharField(max_length=100)
    skill_required = models.FloatField()

    def __str__(self):
        return self.name

class Material(models.Model):

    level = models.ForeignKey(Level, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=100)
    material_type = models.CharField(max_length=1, choices=MATERIAL_TYPES)
    material_length = models.CharField(max_length=1, choices=MATERIAL_LENGTH)
    uploader = models.ForeignKey(User, on_delete=models.CASCADE)
    link = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Student(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    preferred_media = models.CharField(max_length=4, choices=PREFERENCE_TYPES, null=True)
    student_skill = models.FloatField(null=True)
    learned_material = models.ManyToManyField(Material, blank=True)
    took_quiz = models.BooleanField(default=False)
    took_poll = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Question(models.Model):
    level = models.ForeignKey(Level, on_delete=models.DO_NOTHING)
    question = models.CharField(max_length=200)
    op1 = models.CharField(max_length=100)
    op2 = models.CharField(max_length=100)
    op3 = models.CharField(max_length=100)
    op4 = models.CharField(max_length=100)
    op5 = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)

    def __str__(self):
        return self.question


class Poll(models.Model):
    poll = models.CharField(max_length=100)
    op1 = models.CharField(max_length=100)
    op2 = models.CharField(max_length=100)
    op3 = models.CharField(max_length=100)
    op4 = models.CharField(max_length=100)

    def __str__(self):
        return self.poll


class Score(models.Model):
    level = models.ForeignKey(Level, on_delete=models.DO_NOTHING)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return "Level" + str(int(self.level.skill_required)) + self.student.user.username

