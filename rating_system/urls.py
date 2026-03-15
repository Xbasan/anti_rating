from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', views.main_page, name='main'),
    path('news/', views.news_page, name='news'),
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.ico')),
    path('complaint/', views.complaint_page, name='complaint'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/students/', views.get_students_by_group, name='api_students'),
    path('student_list/<str:id_group>/', views.get_students_by_group, name='student_list'),
    path('student_complains/<str:student_name>/', views.student_list_by_name, name='student_complains'),
    path('group_complains/<str:group_name>/', views.group_list_by_name, name='group_complains'),
]
