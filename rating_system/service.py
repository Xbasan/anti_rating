# service.py - должен быть таким
from django.db.models import Q
from .models import RiskZone, Student

class RiskService:
    """Сервис для работы с зонами риска"""
    
    @staticmethod
    def get_zone_for_score(score):
        """Возвращает зону риска для заданного количества баллов"""
        try:
            return RiskZone.objects.filter(
                min_score__lte=score,
                max_score__gte=score
            ).first()
        except RiskZone.DoesNotExist:
            return None
    
    @staticmethod
    def get_zone_name_for_score(score):
        """Возвращает название зоны риска для баллов"""
        zone = RiskService.get_zone_for_score(score)
        return zone.zone_name if zone else "Наблюдение"
    
    @staticmethod
    def get_coefficient_for_score(score):
        """Возвращает коэффициент для баллов"""
        zone = RiskService.get_zone_for_score(score)
        return float(zone.coefficient) if zone else 1.0


class StudentService:
    """Сервис для работы со студентами"""
    
    @staticmethod
    def get_students_with_risk(curator_id=None, group_id=None):
        """Возвращает студентов с информацией о зоне риска"""
        students = Student.objects.filter(Q(is_active=True) & Q(total_score__gt=0.1)).order_by("-total_score")
        
        
        # Фильтры по группе и по куратору зачемто
        if curator_id:
            students = students.filter(curator_id=curator_id)
        if group_id:
            students = students.filter(group_id=group_id)
        
       
        # Добавляем информацию о зоне риска
        result = []
        print()
        for student in students:
        
            # уменщи количество запросов в эту таблицу до 1 
            zone = RiskService.get_zone_for_score(student.total_score)
            
            # Определяем CSS класс
            if zone:
                zone_name = zone.zone_name
                if zone_name in ['Высокий риск исключения', 'Риск исключения']:
                    css_class = "status--danger"
                elif zone_name == 'Предупреждение':
                    css_class = "status--warning"
                else:
                    css_class = "status--safe"
            else:
                zone_name = "Наблюдение"
                css_class = "status--safe"
            
            result.append({
                'student': student,
                'risk_zone': zone,
                'risk_status': zone_name,
                'coefficient': float(zone.coefficient) if zone else 1.0,
                'css_class': css_class  # ← ДОБАВИЛИ!
            })
        
        return result
    
class ComplaintService:
    """Сервис для работы с жалобами"""
    
    @staticmethod
    def create_complaint(user, group_id, student_id, complaint_type_id, explanation):
        """Создает новую жалобу"""
        from .models import Group, Student, ComplaintType, Complaint
        
        # Проверяем данные
        if not all([group_id, student_id, complaint_type_id, explanation]):
            raise ValueError("Все поля должны быть заполнены")
        
        # Получаем объекты
        group = Group.objects.get(id=group_id)
        student = Student.objects.get(id=student_id)
        complaint_type = ComplaintType.objects.get(id=complaint_type_id)
        
        # Получаем TeacherProfile пользователя
        teacher_profile = user.teacher_profile
        
        # Создаем жалобу
        complaint = Complaint.objects.create(
            user=teacher_profile,
            group=group,
            student=student,
            complaint_type=complaint_type,
            explanation=explanation.strip(),
            calculated_score=complaint_type.score,
            status='pending'
        )
        
        return complaint
