from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Task, Category, TaskAttachment
from .forms import TaskForm, CategoryForm, AttachmentForm
from django.utils import timezone
from datetime import timedelta, datetime
from datetime import date
from notifications.utils import notify_task_created, notify_task_updated, notify_task_completed
from django.core.paginator import Paginator
from django.db import models
from celery import shared_task
from django.core.mail import send_mail

@login_required
def task_list(request):
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    # Get per_page parameter or default to 10
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
        if per_page not in [5, 10, 25, 50, 100]:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10
    
    # Start with all tasks for the current user
    tasks = Task.objects.filter(user=request.user).order_by('-created_at')
    
    # Apply filters
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if priority_filter:
        tasks = tasks.filter(priority=priority_filter)
    
    if category_filter:
        tasks = tasks.filter(category_id=category_filter)
    
    if search_query:
        tasks = tasks.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Get all categories for the filter dropdown
    all_categories = Category.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).order_by('name')
    
    # Paginate tasks
    paginator = Paginator(tasks, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tasks': page_obj,
        'all_categories': all_categories,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'per_page': per_page,
    }
    
    return render(request, 'tasks/task_list.html', context)

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    attachments = task.attachments.all()
    
    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.task = task
            attachment.save()
            messages.success(request, 'Attachment added successfully!')
            return redirect('task_detail', pk=task.pk)
    else:
        form = AttachmentForm()
    
    context = {
        'task': task,
        'attachments': attachments,
        'form': form,
    }
    return render(request, 'tasks/task_detail.html', context)

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            
            # Debug: Print task data
            print(f"Creating task: {task.title}")
            print(f"Category: {task.category}")
            
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
        else:
            # Debug: Print form errors
            print("Form errors:", form.errors)
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(user=request.user)
        # Debug: Print category queryset
        print(f"Category queryset for user {request.user}: {form.fields['category'].queryset}")
    
    context = {
        'form': form,
        'title': 'Create New Task'
    }
    return render(request, 'tasks/task_form.html', context)

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_detail', pk=task.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TaskForm(instance=task, user=request.user)
        # Debug: Print category queryset
        print(f"Category queryset for update: {form.fields['category'].queryset}")
    
    context = {
        'form': form,
        'title': 'Update Task',
        'task': task,
    }
    return render(request, 'tasks/task_form.html', context)



@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_list')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if task.status != 'completed':
        task.status = 'completed'
        task.save()  # This will trigger completion notification
        
        # Send additional notification
        notify_task_completed(task)
        
        messages.success(request, 'Task marked as completed!')
    
    return redirect('task_list')

@login_required
def dashboard(request):
    # Get statistics
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, status='completed').count()
    pending_tasks = Task.objects.filter(user=request.user, status='pending').count()
    in_progress_tasks = Task.objects.filter(user=request.user, status='in_progress').count()
    
    # Overdue tasks
    overdue_tasks = Task.objects.filter(
        user=request.user,
        status__in=['pending', 'in_progress'],
        due_date__lt=date.today()
    ).count()
    
    # Priority statistics
    high_priority_tasks = Task.objects.filter(user=request.user, priority='high').count()
    medium_priority_tasks = Task.objects.filter(user=request.user, priority='medium').count()
    low_priority_tasks = Task.objects.filter(user=request.user, priority='low').count()
    
    # Recent tasks with pagination
    recent_per_page = request.GET.get('recent_per_page', 10)
    try:
        recent_per_page = int(recent_per_page)
        if recent_per_page not in [5, 10, 15, 20]:
            recent_per_page = 10
    except (ValueError, TypeError):
        recent_per_page = 10
    
    recent_tasks_list = Task.objects.filter(user=request.user).order_by('-created_at')
    
    # Paginate recent tasks
    paginator = Paginator(recent_tasks_list, recent_per_page)
    recent_page_number = request.GET.get('recent_page')
    recent_tasks_page = paginator.get_page(recent_page_number)
    
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'overdue_tasks': overdue_tasks,
        'high_priority_tasks': high_priority_tasks,
        'medium_priority_tasks': medium_priority_tasks,
        'low_priority_tasks': low_priority_tasks,
        'recent_tasks': recent_tasks_page,
        'recent_per_page': recent_per_page,
    }
    
    return render(request, 'tasks/dashboard.html', context)

@login_required
def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('task_list')
    else:
        form = CategoryForm()
    
    return render(request, 'tasks/category_form.html', {'form': form})


@login_required
def manage_categories(request):
    # Get per_page parameter from GET request or default to 10
    per_page = request.GET.get('per_page', 10)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 10
    
    # Get categories for the current user plus global categories
    categories = Category.objects.filter(
        models.Q(user=request.user) | models.Q(user__isnull=True)
    ).order_by('name')
    
    # Paginate categories
    paginator = Paginator(categories, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'categories': page_obj,  # Pass page object instead of queryset
        'per_page': per_page,
    }
    return render(request, 'tasks/manage_categories.html', context)

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    # Check if category is being used by any task
    if category.tasks.exists():
        messages.error(request, 'Cannot delete category that is being used by tasks!')
        return redirect('manage_categories')
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('manage_categories')
    
    return render(request, 'tasks/confirm_delete_category.html', {'category': category})


@login_required
def update_category(request, pk):
    """Update an existing category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('manage_categories')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        'title': 'Update Category'
    }
    return render(request, 'tasks/category_form.html', context)


@login_required
def delete_attachment(request, pk):
    """Delete a task attachment"""
    attachment = get_object_or_404(TaskAttachment, pk=pk)
    
    # Check if the attachment belongs to a task owned by the user
    if attachment.task.user != request.user:
        messages.error(request, 'You do not have permission to delete this attachment.')
        return redirect('task_list')
    
    task_pk = attachment.task.pk
    
    if request.method == 'POST':
        attachment.delete()
        messages.success(request, 'Attachment deleted successfully!')
    
    return redirect('task_detail', pk=task_pk)


@shared_task
def send_welcome_email(user_email, username):
    """ব্যবহারকারীকে স্বাগতম ইমেইল পাঠানো"""
    subject = f'Welcome {username} to Task Manager!'
    message = 'Thank you for joining our task management system.'
    send_mail(subject, message, 'admin@taskmanager.com', [user_email])
    return f'Email sent to {user_email}'

@shared_task
def cleanup_old_tasks():
    """60 দিনের পুরোনো টাস্ক ডিলিট করা"""
    
    old_date = timezone.now() - timedelta(days=60)
    deleted_count = Task.objects.filter(created_at__lt=old_date).delete()[0]
    return f'Deleted {deleted_count} old tasks'
