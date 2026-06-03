import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import OneTimeCode, Post, Response, Category
from django.conf import settings



# --- БЛОК АВТОРИЗАЦИИ И РЕГИСТРАЦИИ ---
def register(request):
    if request.method == 'POST':
        data = request.POST
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # 1. Проверяем строго по отдельности, чтобы выдать точную ошибку
        if User.objects.filter(username=username).exists():
            return render(request, 'board/register.html', {'error': 'Это имя пользователя уже занято'})

        if User.objects.filter(email=email).exists():
            return render(request, 'board/register.html', {'error': 'Пользователь с таким email уже зарегистрирован'})

        # 2. Если всё чисто — создаем неактивного пользователя
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )

        # 3. Генерируем код
        code_str = str(random.randint(100000, 999999))
        OneTimeCode.objects.create(user=user, code=code_str)

        # 4. Отправляем почту
        send_mail(
            'Код активации',
            f'Код: {code_str}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )

        request.session['pre_active_user_id'] = user.id
        return redirect('verify')

    return render(request, 'board/register.html')


def verify_code(request):
    user_id = request.session.get('pre_active_user_id')
    if not user_id: return redirect('register')
    if request.method == 'POST':
        input_code = request.POST.get('code')
        user = get_object_or_404(User, id=user_id)
        code_entry = OneTimeCode.objects.filter(user=user, code=input_code).last()
        if code_entry:
            user.is_active = True
            user.save()
            code_entry.delete()
            del request.session['pre_active_user_id']
            return redirect('login')
        return render(request, 'board/verify.html', {'error': 'Неверный код'})
    return render(request, 'board/verify.html')


# --- БЛОК ОБЪЯВЛЕНИЙ ---
def about(request):
    return render(request, 'board/about.html')


def home(request):
    # Оптимальная загрузка постов с авторами и категориями за 1 запрос
    posts = Post.objects.all().select_related('author', 'category').order_by('-created_at')
    return render(request, 'board/home.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST' and request.user.is_authenticated:
        # ТЗ: Возможность отправлять отклики к объявлениям других пользователей
        Response.objects.create(author=request.user, post=post, text=request.POST.get('text'))
        return redirect('post_detail', pk=pk)
    # Оптимизировано: загружаем отклики к этому посту
    responses = post.responses.all().select_related('author')
    return render(request, 'board/post_detail.html', {'post': post, 'responses': responses})


@login_required
def post_create(request):
    if request.method == 'POST':
        category = get_object_or_404(Category, id=request.POST.get('category'))
        Post.objects.create(author=request.user, category=category, title=request.POST.get('title'),
                            text=request.POST.get('text'))
        return redirect('home')
    return render(request, 'board/post_create.html', {'categories': Category.objects.all()})


# --- БЛОК ЛИЧНОГО КАБИНЕТА (ПРИВАТНАЯ СТРАНИЦА) ---
@login_required
def dashboard(request):
    my_posts = Post.objects.filter(author=request.user)
    # Идеальный ORM: Избегаем N+1 через select_related связей поста и автора отклика
    responses = Response.objects.filter(post__author=request.user).select_related('post', 'author')

    # ТЗ: Фильтрация по объявлениям в приватном кабинете
    selected_post_id = request.GET.get('post_filter')
    if selected_post_id:
        responses = responses.filter(post_id=selected_post_id)

    return render(request, 'board/dashboard.html',
                  {'responses': responses, 'my_posts': my_posts, 'selected_post_id': selected_post_id})


@login_required
def accept_response(request, pk):
    response = get_object_or_404(Response, pk=pk, post__author=request.user)
    response.is_accepted = True
    response.save()  # Запустит сигнал на email автору отклика
    return redirect('dashboard')


@login_required
def delete_response(request, pk):
    response = get_object_or_404(Response, pk=pk, post__author=request.user)
    response.delete()
    return redirect('dashboard')


@login_required
def post_edit(request, pk):
    # Находим объявление по ID, проверяя, что автором является текущий пользователь
    post = get_object_or_404(Post, pk=pk, author=request.user)
    categories = Category.objects.all()

    if request.method == 'POST':
        category = get_object_or_404(Category, id=request.POST.get('category'))

        # Обновляем поля модели
        post.title = request.POST.get('title')
        post.category = category
        post.text = request.POST.get('text')
        post.save()

        return redirect('post_detail', pk=post.pk)

    return render(request, 'board/post_edit.html', {
        'post': post,
        'categories': categories
    })

