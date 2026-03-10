from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class TeacherProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('teacher', 'Преподаватель'),
    ]
    
    # ИСПРАВЛЕНО: убрали max_length у OneToOneField
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='teacher_profile'  # Важно: user.teacher_profile
    )
    
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher')
    
    def __str__(self):
        return self.full_name
    
    class Meta:
        verbose_name = 'Профиль преподавателя'
        verbose_name_plural = 'Профили преподавателей'


class ComplaintType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    score = models.IntegerField(unique=True)
    
    def __str__(self):
        return self.name

class Group(models.Model):
    group_name = models.CharField(max_length=20, unique=True)
    curator = models.ForeignKey(
        TeacherProfile, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='taught_groups'
    )
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.group_name

class Student(models.Model):
    student_name = models.CharField(max_length=150)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    curator = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='taught_students')
    total_score = models.IntegerField(default=0)
    last_date_of_change_of_total_score = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.student_name

class RiskZone(models.Model):
    zone_name = models.CharField(max_length=100, unique=True)
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    coefficient = models.DecimalField(max_digits=3, decimal_places=2)
    
    def __str__(self):
        return self.zone_name

class Complaint(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    
    user = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    complaint_type = models.ForeignKey(ComplaintType, on_delete=models.PROTECT)
    explanation = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    calculated_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    def __str__(self):
        return f"Жалоба #{self.id} на {self.student}"
