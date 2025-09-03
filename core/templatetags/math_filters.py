from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplica dois valores"""
    try:
        return Decimal(str(value)) * Decimal(str(arg))
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide dois valores"""
    try:
        if Decimal(str(arg)) == 0:
            return 0
        return Decimal(str(value)) / Decimal(str(arg))
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """Subtrai dois valores"""
    try:
        return Decimal(str(value)) - Decimal(str(arg))
    except (ValueError, TypeError):
        return 0

@register.filter
def add_decimal(value, arg):
    """Soma dois valores com precisão decimal"""
    try:
        return Decimal(str(value)) + Decimal(str(arg))
    except (ValueError, TypeError):
        return 0
