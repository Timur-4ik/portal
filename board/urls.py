from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('register/', views.register, name='register'),
    path('verify/', views.verify_code, name='verify'),
    path('login/', auth_views.LoginView.as_view(template_name='board/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('post/new/', views.post_create, name='post_create'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('response/<int:pk>/accept/', views.accept_response, name='accept_response'),
    path('response/<int:pk>/delete/', views.delete_response, name='delete_response'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),

]
