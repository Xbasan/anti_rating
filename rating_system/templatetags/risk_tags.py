from django import template
from ..service import RiskService

register = template.Library()

@register.filter
def get_risk_zone(score):
    """Возвращает зону риска для баллов"""
    return RiskService.get_zone_for_score(score)

@register.filter
def get_risk_status(score):
    """Возвращает статус риска для баллов"""
    zone = RiskService.get_zone_for_score(score)
    if not zone:
        return "Наблюдение"
    return zone.zone_name

@register.filter
def get_risk_class(score):
    """Возвращает CSS класс для статуса"""
    zone = RiskService.get_zone_for_score(score)
    if not zone:
        return "status--safe"
    
    zone_name = zone.zone_name
    if zone_name in ['Высокий риск исключения', 'Риск исключения']:
        return "status--danger"
    elif zone_name == 'Предупреждение':
        return "status--warning"
    else:
        return "status--safe"