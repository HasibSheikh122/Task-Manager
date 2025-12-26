from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from tasks.models import Task, Category
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import logout as auth_logout

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('dashboard')  # Redirect logged-in users to dashboard
    return render(request, 'home.html')  # Show home page for non-logged-in users

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    # Get task counts
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, status='completed').count()
    pending_tasks = Task.objects.filter(user=request.user, status='pending').count()
    in_progress_tasks = Task.objects.filter(user=request.user, status='in_progress').count()
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('password_change_done')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})

@login_required
def password_change_done(request):
    return render(request, 'accounts/password_change_done.html')


@login_required
def account_delete(request):
    """Show account deletion confirmation page"""
    # Get user statistics
    total_tasks = Task.objects.filter(user=request.user).count()
    total_categories = Category.objects.filter(user=request.user).count()
    
    context = {
        'total_tasks': total_tasks,
        'total_categories': total_categories,
    }
    return render(request, 'accounts/account_delete.html', context)

@login_required
def account_delete_confirm(request):
    """Process account deletion"""
    if request.method == 'POST':
        # Verify password
        password = request.POST.get('password')
        if not request.user.check_password(password):
            messages.error(request, 'Incorrect password. Account deletion cancelled.')
            return redirect('profile')
        
        # Get user data before deletion for message
        username = request.user.username
        email = request.user.email
        
        # Delete the user
        request.user.delete()
        
      
        
        messages.success(request, f'Account for {username} has been permanently deleted.')
        return redirect('home')
    
    return redirect('account_delete')


@login_required
def custom_logout(request):
    """Custom logout view that handles both GET and POST"""
    if request.method == 'POST':
        auth_logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('home')
    else:
        # For GET requests, show a confirmation page
        return render(request, 'accounts/logout_confirm.html')