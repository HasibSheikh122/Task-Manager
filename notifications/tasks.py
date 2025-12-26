from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task
from .utils import notify_task_due_soon, notify_task_overdue

@shared_task
def check_due_tasks():
    """Check for tasks that are due soon or overdue"""
    now = timezone.now()
    
    # Tasks due in next 24 hours
    due_soon_threshold = now + timedelta(hours=24)
    due_soon_tasks = Task.objects.filter(
        due_date__lte=due_soon_threshold,
        due_date__gt=now,
        status__in=['pending', 'in_progress']
    )
    
    for task in due_soon_tasks:
        notify_task_due_soon(task)
    
    # Overdue tasks
    overdue_tasks = Task.objects.filter(
        due_date__lt=now,
        status__in=['pending', 'in_progress']
    )
    
    for task in overdue_tasks:
        notify_task_overdue(task)
    
    return f"Checked {due_soon_tasks.count()} due soon and {overdue_tasks.count()} overdue tasks"

@shared_task
def send_daily_summary():
    """Send daily summary notification to users"""
    from django.contrib.auth.models import User
    from .utils import create_notification
    
    for user in User.objects.filter(is_active=True):
        pending_tasks = Task.objects.filter(user=user, status='pending').count()
        overdue_tasks = Task.objects.filter(
            user=user,
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).count()
        
        message = f"You have {pending_tasks} pending tasks"
        if overdue_tasks > 0:
            message += f" and {overdue_tasks} overdue tasks"
        
        create_notification(
            user=user,
            notification_type='system',
            title='Daily Task Summary',
            message=message
        )
    
    return "Daily summary sent to all users"