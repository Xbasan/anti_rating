from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_page, name='main'),
    path('news/', views.news_page, name='news'),
    path('complaint/', views.complaint_page, name='complaint'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/students/', views.get_students_by_group, name='api_students'),
]