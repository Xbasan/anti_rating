# signals.py - ПОЛНОСТЬЮ ЗАМЕНИТЕ СОДЕРЖИМОЕ
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Student, Complaint, RiskZone
from django.db import transaction

# Для отслеживания изменений статуса между сохранениями
_status_cache = {}
_calculated_score_cache = {}

@receiver(pre_save, sender=Complaint)
def calculate_or_preserve_complaint_score(sender, instance, **kwargs):
    """
    Рассчитывает баллы жалобы при создании или сохраняет существующие.
    """
    # Сохраняем старый статус и calculated_score для сравнения
    if instance.pk:
        try:
            old_instance = Complaint.objects.get(pk=instance.pk)
            _status_cache[instance.pk] = old_instance.status
            _calculated_score_cache[instance.pk] = old_instance.calculated_score
        except Complaint.DoesNotExist:
            _status_cache[instance.pk] = None
            _calculated_score_cache[instance.pk] = 0
    
    # Рассчитываем calculated_score ТОЛЬКО при создании новой жалобы
    # или если жалоба еще не имеет calculated_score
    if (not instance.pk or instance.calculated_score == 0) and instance.student and instance.complaint_type:
        # Базовые баллы из типа жалобы
        base_score = instance.complaint_type.score
        
        # Определяем зону риска студента НА МОМЕНТ СОЗДАНИЯ ЖАЛОБЫ
        try:
            risk_zone = RiskZone.objects.filter(
                min_score__lte=instance.student.total_score,
                max_score__gte=instance.student.total_score
            ).first()
            
            coefficient = risk_zone.coefficient if risk_zone else 1.0
        except RiskZone.DoesNotExist:
            coefficient = 1.0
        
        instance.calculated_score = base_score * coefficient
        print(f"📝 Рассчитан calculated_score: {instance.calculated_score} (база: {base_score}, коэффициент: {coefficient})")
    
    # Если жалоба уже существует и имеет calculated_score - НЕ ПЕРЕСЧИТЫВАЕМ!

@receiver(post_save, sender=Complaint)
def update_student_score_on_status_change(sender, instance, created, **kwargs):
    """
    Обновляет баллы студента при изменении статуса жалобы.
    """
    old_status = _status_cache.get(instance.pk, None)
    old_calculated_score = _calculated_score_cache.get(instance.pk, instance.calculated_score)
    
    print(f"🔍 DEBUG: id={instance.id}, старый статус={old_status}, новый статус={instance.status}, "
          f"calculated_score={instance.calculated_score}, old_calculated_score={old_calculated_score}")
    
    with transaction.atomic():
        # 1. Если статус меняется НА 'approved' (с любого другого статуса)
        if instance.status == 'approved' and old_status != 'approved':
            # Добавляем calculated_score баллов
            student = Student.objects.select_for_update().get(pk=instance.student.pk)
            student.total_score += instance.calculated_score
            student.last_date_of_change_of_total_score = timezone.now()
            student.save(update_fields=['total_score', 'last_date_of_change_of_total_score'])
            
            print(f"✅ Начисление: {student} +{instance.calculated_score} баллов. "
                  f"Новый тотал: {student.total_score}")
        
        # 2. Если статус меняется С 'approved' на что-то другое (отклонено или на рассмотрении)
        elif old_status == 'approved' and instance.status != 'approved':
            # Вычитаем calculated_score баллов (которые были добавлены при одобрении)
            student = Student.objects.select_for_update().get(pk=instance.student.pk)
            student.total_score = max(0, student.total_score - old_calculated_score)
            student.last_date_of_change_of_total_score = timezone.now()
            student.save(update_fields=['total_score', 'last_date_of_change_of_total_score'])
            
            print(f"❌ Списание: {student} -{old_calculated_score} баллов (были добавлены при одобрении). "
                  f"Новый тотал: {student.total_score}")
        
        # 3. Если создается новая жалоба со статусом approved (маловероятно, но на всякий случай)
        elif created and instance.status == 'approved':
            # Добавляем calculated_score баллов
            student = Student.objects.select_for_update().get(pk=instance.student.pk)
            student.total_score += instance.calculated_score
            student.last_date_of_change_of_total_score = timezone.now()
            student.save(update_fields=['total_score', 'last_date_of_change_of_total_score'])
            
            print(f"✅ Создание с одобрением: {student} +{instance.calculated_score} баллов. "
                  f"Новый тотал: {student.total_score}")
        
        # 4. Другие случаи (pending→pending, rejected→rejected, pending↔rejected) - не меняем баллы
        else:
            print(f"⚡ Статус не влияет на баллы: {old_status} → {instance.status}")
    
    # Очищаем кэш
    if instance.pk in _status_cache:
        del _status_cache[instance.pk]
    if instance.pk in _calculated_score_cache:
        del _calculated_score_cache[instance.pk]