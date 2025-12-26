from django import template

register = template.Library()

@register.filter
def tasks_by_status(user, status):
    """Filter user's tasks by status"""
    return user.tasks.filter(status=status)

@register.filter
def task_count_by_status(user, status):
    """Count user's tasks by status"""
    return user.tasks.filter(status=status).count()