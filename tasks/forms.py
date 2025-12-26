from django import forms
from django.db import models
from django.utils import timezone
from .models import Task, Category, TaskAttachment

class TaskForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'id': 'due_date'
            }
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'priority', 'category', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title',
                'id': 'title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter task description',
                'id': 'description'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'status'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-control',
                'id': 'priority'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'id': 'category'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        
        # Filter categories by user (if user is provided)
        if user:
            # Get both user-specific categories and global categories (user=None)
            self.fields['category'].queryset = Category.objects.filter(
                models.Q(user=user) | models.Q(user__isnull=True)
            ).distinct().order_by('name')
        else:
            # Only show global categories
            self.fields['category'].queryset = Category.objects.filter(
                user__isnull=True
            ).order_by('name')
        
        # Set initial due date in correct format
        if self.instance and self.instance.due_date:
            self.initial['due_date'] = self.instance.due_date.strftime('%Y-%m-%dT%H:%M')
        
        # Make category not required
        self.fields['category'].required = False
        
        # Add empty label for category
        self.fields['category'].empty_label = "Select a category (optional)"
        
        # Set choices for status and priority
        self.fields['status'].choices = [
            ('', 'Select status'),
            ('pending', 'Pending'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
        ]
        
        self.fields['priority'].choices = [
            ('', 'Select priority'),
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
        ]

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name',
                'id': 'category_name'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'id': 'category_color',
                'style': 'height: 40px; padding: 0;'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default color if not provided
        if not self.instance.pk and not self.data.get('color'):
            self.initial['color'] = '#007bff'

class AttachmentForm(forms.ModelForm):
    class Meta:
        model = TaskAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'id': 'file_input'
            })
        }