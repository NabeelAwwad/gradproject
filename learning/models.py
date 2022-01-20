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


class Topic(models.Model):
    name = models.CharField(max_length=100)
    dependencies = models.ManyToManyField('Topic', blank=True)

    def __str__(self):
        return self.name


class Poll(models.Model):
    poll = models.CharField(max_length=100)
    op1 = models.CharField(max_length=100)
    op2 = models.CharField(max_length=100)
    op3 = models.CharField(max_length=100)
    op4 = models.CharField(max_length=100)

    def __str__(self):
        return self.poll


class Material(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.DO_NOTHING, default=1)
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
    learned_material = models.ManyToManyField(Material, blank=True)
    passed_topics = models.ManyToManyField(Topic, blank=True)
    took_quiz = models.BooleanField(default=False)
    took_poll = models.BooleanField(default=False)
    ratings = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username


class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.DO_NOTHING, default=1)
    question = models.CharField(max_length=200)
    op1 = models.CharField(max_length=100)
    op2 = models.CharField(max_length=100)
    op3 = models.CharField(max_length=100)
    op4 = models.CharField(max_length=100)
    op5 = models.CharField(max_length=100)
    answer = models.CharField(max_length=100)

    def __str__(self):
        return self.question


class Score(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.DO_NOTHING, default=1)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.topic.name + self.student.user.username

