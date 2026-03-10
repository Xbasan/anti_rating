from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Func, FloatField
from django.db.models import F, Func, Value
from .models import Student, Complaint, Group, ComplaintType, User  # ← ДОБАВЬ User
from .service import StudentService, ComplaintService

# 1. Главная страница
def main_page(request):
    # 1. Используем сервис для получения студентов с рисками
    students_data = StudentService.get_students_with_risk()
    
    # 2. Поиск (если нужен)
    search = request.GET.get('search', '')
    if search:
        filtered_data = []
        for data in students_data:
            if search.lower() in data['student'].student_name.lower():
                filtered_data.append(data)
        students_data = filtered_data
    
    # 3. Переименуем переменную для шаблона
    return render(request, 'main.html', {
        'students_with_risk': students_data,  # ← переименовали!
        'search_query': search,
    })

# 2. Страница новостей (жалоб)
def news_page(request):
    # Все жалобы с информацией
    complaints = Complaint.objects.select_related(
        'student', 'complaint_type', 'user'
    ).order_by('-date')  # ← новые сверху
    
    return render(request, 'news.html', {'complaints': complaints})

# 3. Вход в систему
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('main')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

# 4. Выход
def logout_view(request):
    auth_logout(request)
    return redirect('main')

# 5. Форма жалобы (ТОЛЬКО для авторизованных)
@login_required(login_url='/login/')
def complaint_page(request):
    groups = Group.objects.filter(is_active=True)
    complaint_types = ComplaintType.objects.all()
    
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            group_id = request.POST.get('group_id')
            student_id = request.POST.get('student_id')
            complaint_type_id = request.POST.get('type_id')
            explanation = request.POST.get('explanation')
            
            # Используем сервис для создания жалобы
            complaint = ComplaintService.create_complaint(
                user=request.user,
                group_id=group_id,
                student_id=student_id,
                complaint_type_id=complaint_type_id,
                explanation=explanation
            )
            
            messages.success(request, '✅ Жалоба успешно отправлена на рассмотрение!')
            return redirect('complaint')
            
        except ValueError as e:
            messages.error(request, f'❌ {str(e)}')
        except (Group.DoesNotExist, Student.DoesNotExist, ComplaintType.DoesNotExist) as e:
            messages.error(request, '❌ Ошибка данных. Проверьте выбранные значения.')
        except AttributeError as e:
            messages.error(request, '❌ У вас нет профиля преподавателя. Обратитесь к администратору.')
        except Exception as e:
            messages.error(request, f'❌ Системная ошибка: {str(e)[:100]}')
    
    return render(request, 'complaint.html', {
        'groups': groups,
        'complaint_types': complaint_types,
    })

# 6. API для получения студентов (для JavaScript)
@csrf_exempt
def get_students_by_group(request):
    group_id = request.GET.get('group_id')
    
    if not group_id:
        return JsonResponse({'error': 'Не указана группа'}, status=400)
    
    students = Student.objects.filter(
        group_id=group_id,
        is_active=True
    ).values('id', 'student_name')
    
    return JsonResponse({
        'students': list(students)
    })

# API методы для зависимых выпадающих списков (AJAX)
def student_list_by_groups(request, id_group):
    students = Student.objects.filter(group_id=id_group, is_active=True).values(
        'id', 'student_name'
    )
    return JsonResponse(list(students), safe=False)


# Поиск жалоб по имени студента (с использованием сходства строк)
class Similarity(Func):
    function = 'similarity'
    output_field = FloatField()

def student_list_by_name(request, student_name):
    complaints = Complaint.objects.annotate(
        similarity_score=Similarity(F('student__student_name'), student_name)
    ).filter(
        similarity_score__gte=0.3
    ).values(
        'id', 'explanation', 'date', 'status',
        student_name=F('student__student_name'),
        group_name=F('group__group_name'),
        user_name=F('user__full_name')
    ).order_by('-similarity_score', '-id')

    title = complaints[0]["student_name"] if complaints.exists() else f"Нет жалоб на {student_name}"
        
    context = {
        'complains_data': complaints,
        'title': title,
    }
    return render(request, "core/news.html", context)


def group_list_by_name(request, group_name):
    complaints = Complaint.objects.filter(
        group__group_name__iexact=group_name
    ).values(
        'id', 'explanation', 'date', 'status',
        student_name=F('student__student_name'),
        group_name=F('group__group_name'),
        user_name=F('user__full_name')
    ).order_by('-id')

    title = group_name if complaints.exists() else f"Нет жалоб для группы {group_name}"
        
    context = {
        'complains_data': complaints,
        'title': title,
    }
    return render(request, "core/news.html", context)
