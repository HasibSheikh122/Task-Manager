from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from .models import Notification
from django.utils import timezone
import json

def create_notification(user, notification_type, title, message, related_id=None, related_url=''):
    """Create and send real-time notification"""
    
    # Create notification in database
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        related_id=related_id,
        related_url=related_url
    )
    
    # Send real-time notification via WebSocket
    send_real_time_notification(user, notification)
    
    return notification

def send_real_time_notification(user, notification):
    """Send notification through WebSocket"""
    channel_layer = get_channel_layer()
    
    async_to_sync(channel_layer.group_send)(
        f'user_{user.id}',
        {
            'type': 'send_notification',
            'notification': {
                'id': notification.id,
                'type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'icon': notification.icon,
                'related_url': notification.related_url,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_read': notification.is_read,
            }
        }
    )

def notify_task_created(task):
    """Send notification for task creation"""
    create_notification(
        user=task.user,
        notification_type='task_created',
        title='New Task Created',
        message=f'Task "{task.title}" has been created.',
        related_id=task.id,
        related_url=f'/tasks/{task.id}/'
    )

def notify_task_updated(task):
    """Send notification for task update"""
    create_notification(
        user=task.user,
        notification_type='task_updated',
        title='Task Updated',
        message=f'Task "{task.title}" has been updated.',
        related_id=task.id,
        related_url=f'/tasks/{task.id}/'
    )

def notify_task_completed(task):
    """Send notification for task completion"""
    create_notification(
        user=task.user,
        notification_type='task_completed',
        title='Task Completed',
        message=f'Task "{task.title}" has been completed.',
        related_id=task.id,
        related_url=f'/tasks/{task.id}/'
    )

def notify_task_due_soon(task):
    """Send notification for due soon task"""
    create_notification(
        user=task.user,
        notification_type='task_due',
        title='Task Due Soon',
        message=f'Task "{task.title}" is due soon.',
        related_id=task.id,
        related_url=f'/tasks/{task.id}/'
    )

def notify_task_overdue(task):
    """Send notification for overdue task"""
    create_notification(
        user=task.user,
        notification_type='task_overdue',
        title='Task Overdue',
        message=f'Task "{task.title}" is overdue.',
        related_id=task.id,
        related_url=f'/tasks/{task.id}/'
    )

def notify_all_users(title, message, notification_type='system'):
    """Send notification to all users"""
    users = User.objects.filter(is_active=True)
    for user in users:
        create_notification(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message
        )