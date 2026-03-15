from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import TeacherProfile, ComplaintType, Group, Student, RiskZone, Complaint

# ==================== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ====================

# 1. Отключаем стандартного User
admin.site.unregister(User)

# 2. Создаём встроенный профиль для User
class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = 'Профиль преподавателя'
    fields = ('full_name', 'role')
    
    # Автоматически заполняем full_name из User
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj and obj.pk:
            # Заполняем full_name из данных User
            formset.form.base_fields['full_name'].initial = obj.get_full_name() or obj.username
        return formset

# 3. Кастомизированный UserAdmin
class CustomUserAdmin(BaseUserAdmin):
    inlines = (TeacherProfileInline,)
    
    # В списке пользователей
    list_display = ('username', 'get_full_name', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'teacher_profile__role')  # ← исправлено: teacher_profile
    
    def get_full_name(self, obj):
        # Используем related_name 'teacher_profile'
        if hasattr(obj, 'teacher_profile'):
            return obj.teacher_profile.full_name
        return obj.username
    get_full_name.short_description = 'ФИО'
    
    # Поля при редактировании
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

# 4. Регистрируем кастомизированного User
admin.site.register(User, CustomUserAdmin)

# 5. Отдельная админка для TeacherProfile (если нужна)
@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'get_username', 'role')  # ← исправлено
    list_filter = ('role',)
    search_fields = ('full_name', 'user__username')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Логин'

# ==================== ОСТАЛЬНЫЕ МОДЕЛИ ====================

@admin.register(ComplaintType)
class ComplaintTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'score')
    ordering = ('score',)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_name', 'curator', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('group_name',)
    
    
    # Ограничиваем выбор куратора
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "curator":
            # Сортируем по ФИО
            kwargs["queryset"] = TeacherProfile.objects.filter(
                role__in=['teacher', 'admin']
            ).order_by('full_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'group', 'curator', 'total_score', 'is_active')
    list_filter = ('group', 'is_active')
    search_fields = ('student_name', 'group__group_name')
    readonly_fields = ('curator',)
    
    
    def save_model(self, request, obj, form, change):
        # Автоматически ставим куратора из группы
        if obj.group and obj.group.curator:
            obj.curator = obj.group.curator
        super().save_model(request, obj, form, change)
    
    # Ограничиваем выбор куратора
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "curator":
            kwargs["queryset"] = TeacherProfile.objects.filter(
                role__in=['teacher', 'admin']
            ).order_by('full_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(RiskZone)
class RiskZoneAdmin(admin.ModelAdmin):
    list_display = ('zone_name', 'min_score', 'max_score', 'coefficient')
    ordering = ('min_score',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    # Добавляем status в список отображаемых полей
    list_display = ('id', 'student', 'get_user_name', 'complaint_type', 'status', 'date')
    
    # 1. ПОЗВОЛЯЕТ МЕНЯТЬ СТАТУС ПРЯМО В ТАБЛИЦЕ (БЕЗ ПЕРЕХОДА ВНУТРЬ ЗАПИСИ)
    list_editable = ('status',) 
    
    list_filter = ('status', 'complaint_type', 'date')
    search_fields = ('student__student_name', 'explanation')
    date_hierarchy = 'date'

    # 2. ГРУППОВЫЕ ДЕЙСТВИЯ (ВЫПАДАЮЩИЙ СПИСОК "ДЕЙСТВИЕ")
    actions = ['set_approved', 'set_rejected', 'set_pending']

    @admin.action(description='Изменить статус на "Одобрено"')
    def set_approved(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f'Обновлено записей: {updated}. Статус: Одобрено.')

    @admin.action(description='Изменить статус на "Отклонено"')
    def set_rejected(self, request, queryset):
        updated = queryset.update(status='rejected')
        self.message_user(request, f'Обновлено записей: {updated}. Статус: Отклонено.')

    @admin.action(description='Изменить статус на "На рассмотрении"')
    def set_pending(self, request, queryset):
        updated = queryset.update(status='pending')
        self.message_user(request, f'Обновлено записей: {updated}. Статус: На рассмотрении.')

    # --- ВАШИ СУЩЕСТВУЮЩИЕ МЕТОДЫ ---
    
    def get_user_name(self, obj):
        if obj.user and hasattr(obj.user, 'teacher_profile'):
            return obj.user.teacher_profile.full_name
        return 'Неизвестно'
    get_user_name.short_description = 'Преподаватель'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = TeacherProfile.objects.filter(
                role__in=['teacher', 'admin']
            ).order_by('full_name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
