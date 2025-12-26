from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('task_created', 'Task Created'),
        ('task_updated', 'Task Updated'),
        ('task_completed', 'Task Completed'),
        ('task_due', 'Task Due Soon'),
        ('task_overdue', 'Task Overdue'),
        ('task_assigned', 'Task Assigned'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    related_id = models.IntegerField(null=True, blank=True)  # For linking to task, etc.
    related_url = models.CharField(max_length=200, blank=True)
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    @property
    def icon(self):
        icons = {
            'task_created': 'fas fa-plus-circle text-primary',
            'task_updated': 'fas fa-edit text-info',
            'task_completed': 'fas fa-check-circle text-success',
            'task_due': 'fas fa-clock text-warning',
            'task_overdue': 'fas fa-exclamation-triangle text-danger',
            'task_assigned': 'fas fa-user-plus text-primary',
            'system': 'fas fa-cog text-secondary',
        }
        return icons.get(self.notification_type, 'fas fa-bell')