from django.contrib import admin
from .models import Category, Task, TaskAttachment

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'user', 'created_at')
    list_filter = ('user',)
    search_fields = ('name',)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'priority', 'category', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'category', 'user')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'

class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'task', 'file_type', 'file_size', 'uploaded_at')
    list_filter = ('file_type',)
    search_fields = ('filename', 'task__title')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskAttachment, TaskAttachmentAdmin)
