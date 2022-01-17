from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from learning.forms import UserRegisterForm, UserUpdateForm
from django.shortcuts import render, redirect
from learning.models import Question, Student, Poll, Material, User, Level, Score
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Q


@login_required
def home(request):
    student = request.user.student
    if not student.took_poll:
        return redirect('poll')
    if not student.took_quiz:
        return redirect('quiz')
    preference = student.get_preferred_media_display()
    learned = student.learned_material.all()
    print('learned', learned)
    misconceptions = Material.objects.filter(level__skill_required__lt=student.student_skill)
    materials = Material.objects.filter(level__skill_required__exact=student.student_skill, material_length='L')
    for mat in learned:
        materials = materials.exclude(name__exact=mat.name)
    student_scores = Score.objects.filter(student=student)
    for score in student_scores:
        if score.score == 1:
            misconceptions = misconceptions.exclude(level=score.level, material_length__exact='L')
        elif score.score == 0 or score.score == 2:
            misconceptions = misconceptions.exclude(level=score.level)

    for mat in learned:
        misconceptions = misconceptions.exclude(name__exact=mat.name)

    if len(student.preferred_media) == 1:
        materials = materials.filter(material_type__exact=student.preferred_media)
        misconceptions = misconceptions.filter(material_type__exact=student.preferred_media)
    elif len(student.preferred_media) == 2:
        materials = materials.filter(Q(material_type__exact=student.preferred_media[0])
                                     | Q(material_type__exact=student.preferred_media[1]))
        misconceptions = misconceptions.filter(Q(material_type__exact=student.preferred_media[0])
                                               | Q(material_type__exact=student.preferred_media[1]))
    elif len(student.preferred_media) == 3:
        materials = materials.filter(Q(material_type__exact=student.preferred_media[0])
                                     | Q(material_type__exact=student.preferred_media[1])
                                     | Q(material_type__exact=student.preferred_media[2]))
        misconceptions = misconceptions.filter(Q(material_type__exact=student.preferred_media[0])
                                               | Q(material_type__exact=student.preferred_media[1])
                                               | Q(material_type__exact=student.preferred_media[2]))

    if not materials and student.student_skill != 9:
        student.student_skill += 1
        student.save()
        return redirect('home')

    if request.method == 'POST':
        for mat in materials:
            if mat.name in request.POST:
                student.learned_material.add(mat)
                student.save()
        for mat in misconceptions:
            if mat.name in request.POST:
                student.learned_material.add(mat)
        return redirect("home")
    else:
        learned = student.learned_material.all()
        context = {
            'materials': materials,
            'misconceptions': misconceptions,
            'learned': learned,
            'preference': preference,
            'took_quiz': request.user.student.took_quiz,
            'took_poll': request.user.student.took_poll,
        }
        return render(request, 'home.html', context)


def register(request):
    if request.user.is_authenticated:
        return redirect(request.POST.get('next', '/'))
    return render(request, 'Register.html')


def student_register(request):
    if request.user.is_authenticated:
        return redirect(request.POST.get('next', '/'))
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.is_student = True
            user.save()
            student = Student.objects.create(user=user)
            student.save()
            login(request, user)
            return redirect('poll')
        else:
            messages.error(request, user_form.errors)
    else:
        user_form = UserRegisterForm()
    return render(request, 'StudentRegister.html', {'user_form': user_form})


def teacher_register(request):
    return redirect("register")
    # if request.method == 'POST':
    #     user_form = UserRegisterForm(request.POST)
    #     if user_form.is_valid():
    #         user = user_form.save()
    #         user.save()
    #         login(request, user)
    #         return redirect('home')
    # else:
    #     user_form = UserRegisterForm()
    # return render(request, 'TeacherRegister.html', {'user_form': user_form})


@login_required
def poll(request):
    polls = Poll.objects.all()
    student = request.user.student
    # global score_au, score_vi, score_rw, score_ki
    score_v = 0
    score_a = 0
    score_r = 0
    score_k = 0
    unanswered = 0
    if request.method == 'POST':
        context = {
            'polls': polls,
            'took_quiz': request.user.student.took_quiz,
            'took_poll': request.user.student.took_poll,
        }
        for p in polls:
            answers = request.POST.getlist(p.poll)
            print(answers)
            if 'op1' in answers:
                score_v += 1
            if 'op2' in answers:
                score_a += 1
            if 'op3' in answers:
                score_r += 1
            if 'op4' in answers:
                score_k += 1
            if not answers:
                unanswered += 1
        score_sum = score_v + score_a + score_r + score_k
        if unanswered > 4:
            messages.error(request, "Please answer at least 12 questions, so that we can give you a more accurate "
                                    "idea of your learning preferences.")
        else:
            if (score_v - score_a) / score_sum > 0.1 and (score_v - score_r) / score_sum > 0.1 \
                    and (score_v - score_k) / score_sum > 0.1:
                student.preferred_media = 'V'
            elif (score_a - score_v) / score_sum > 0.1 and (score_a - score_r) / score_sum > 0.1 \
                    and (score_a - score_k) / score_sum > 0.1:
                student.preferred_media = 'A'
            elif (score_r - score_v) / score_sum > 0.1 and (score_r - score_a) / score_sum > 0.1 \
                    and (score_r - score_k) / score_sum > 0.1:
                student.preferred_media = 'R'
            elif (score_k - score_v) / score_sum > 0.1 and (score_k - score_a) / score_sum > 0.1 \
                    and (score_k - score_r) / score_sum > 0.1:
                student.preferred_media = 'K'
            elif abs((score_v - score_a) / score_sum) < 0.1 and (score_a - score_r) / score_sum > 0.1 \
                    and (score_a - score_k) / score_sum > 0.1:
                student.preferred_media = 'VA'
            elif abs((score_v - score_r) / score_sum) < 0.1 and (score_v - score_a) / score_sum > 0.1 \
                    and (score_v - score_k) / score_sum > 0.1:
                student.preferred_media = 'VR'
            elif abs((score_v - score_k) / score_sum) < 0.1 and (score_v - score_a) / score_sum > 0.1 \
                    and (score_v - score_r) / score_sum > 0.1:
                student.preferred_media = 'VK'
            elif abs((score_a - score_r) / score_sum) < 0.1 and (score_a - score_v) / score_sum > 0.1 \
                    and (score_a - score_k) / score_sum > 0.1:
                student.preferred_media = 'AR'
            elif abs((score_a - score_k) / score_sum) < 0.1 and (score_a - score_v) / score_sum > 0.1 \
                    and (score_a - score_r) / score_sum > 0.1:
                student.preferred_media = 'AK'
            elif abs((score_r - score_k) / score_sum) < 0.1 and (score_r - score_v) / score_sum > 0.1 \
                    and (score_r - score_a) / score_sum > 0.1:
                student.preferred_media = 'RK'
            elif abs((score_v - score_r) / score_sum) < 0.1 and abs((score_v - score_a)) / score_sum < 0.1 \
                    and (score_v - score_k) / score_sum > 0.1:
                student.preferred_media = 'VAR'
            elif abs((score_v - score_a) / score_sum) < 0.1 and abs((score_v - score_k)) / score_sum < 0.1 \
                    and (score_v - score_r) / score_sum > 0.1:
                student.preferred_media = 'VAK'
            elif abs((score_v - score_r) / score_sum) < 0.1 and abs((score_v - score_k)) / score_sum < 0.1 \
                    and (score_v - score_a) / score_sum > 0.1:
                student.preferred_media = 'VRK'
            elif abs((score_a - score_r) / score_sum) < 0.1 and abs((score_a - score_k)) / score_sum < 0.1 \
                    and (score_a - score_v) / score_sum > 0.1:
                student.preferred_media = 'ARK'
            else:
                student.preferred_media = 'VARK'
            if not student.took_poll:
                student.took_poll = True
                student.save()
                return redirect('quiz')
            else:
                student.save()
                return redirect('home')
    else:
        context = {
            'polls': polls,
            'took_quiz': request.user.student.took_quiz,
            'took_poll': request.user.student.took_poll,
        }
    return render(request, 'poll.html', context)


@login_required
def quiz(request):
    if request.user.student.took_quiz and request.user.student.student_skill != 9:
        return redirect(request.POST.get('next', '/'))

    if not request.user.student.took_poll:
        return redirect('poll')
    if request.method == 'POST':
        questions = Question.objects.all()
        student = request.user.student
        student.student_skill = 1
        unanswered = 0

        # set scores to 0
        student_scores = Score.objects.filter(student=student)
        for score in student_scores:
            score.score = 0
            score.save()

        for q in questions:
            if request.POST.get(q.question) is None:
                unanswered += 1

        if unanswered > 0:
            messages.error(request, "Please answer all of the questions.")
            return redirect("quiz")

        for q in questions:
            if Score.objects.filter(student=student, level=q.level).exists():
                score = Score.objects.get(student=student, level=q.level)
            else:
                score = Score.objects.create(student=student, level=q.level)
            if q.answer == request.POST.get(q.question):
                score.score += 1
            if score.score != 0:
                student.student_skill = q.level.skill_required + 1
            else:
                break

            score.save()
        student.took_quiz = True
        student.save()
        return redirect('home')
    else:
        questions = Question.objects.all()
        context = {
            'questions': questions,
            'took_quiz': request.user.student.took_quiz,
            'took_poll': request.user.student.took_poll,
        }
    return render(request, 'Quiz.html', context)


@login_required
def update(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'your account has been updated!')
            # return redirect('home')
        else:
            messages.error(request, u_form.errors)
    else:
        u_form = UserUpdateForm(instance=request.user)
    context = {
        'u_form': u_form,
        'took_quiz': request.user.student.took_quiz,
        'took_poll': request.user.student.took_poll,

    }
    return render(request, 'update.html', context)


@login_required
def change_pass(request):
    if request.method == 'POST':
        pass_form = PasswordChangeForm(request.user, request.POST)
        if pass_form.is_valid():
            user = pass_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated!')
            # return redirect('home')
        else:
            messages.error(request, pass_form.errors)
    else:
        pass_form = PasswordChangeForm(request.user, request.POST)
    context = {
        'pass_form': pass_form,
        'took_quiz': request.user.student.took_quiz,
        'took_poll': request.user.student.took_poll,
    }
    return render(request, 'change_pass.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect(request.POST.get('next', '/'))
    if request.method == 'POST':

        auth_form = AuthenticationForm(data=request.POST)
        username = request.POST['username']
        password = request.POST['password']
        if auth_form.is_valid():
            user = authenticate(request, username=username, password=password)
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Please enter a correct username and password."
                                    " Note that both fields may be case-sensitive.")
    else:
        auth_form = AuthenticationForm(data=request.POST)
    context = {
        'auth_form': auth_form
    }
    return render(request, 'Login.html', context)


def about(request):
    if request.user.is_authenticated:
        context = {
            'took_quiz': request.user.student.took_quiz,
            'took_poll': request.user.student.took_poll,
        }
    else:
        context = {}
    return render(request, "about.html", context)
