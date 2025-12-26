from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from accounts import views as account_views
from django.contrib.auth.views import LogoutView
from django.views.decorators.csrf import csrf_exempt

# Allow GET requests for logout
class CustomLogoutView(LogoutView):
    http_method_names = ['get', 'post', 'options']

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Home page
    path('', account_views.home, name='home'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('register/', account_views.register, name='register'),
    path('profile/', account_views.profile, name='profile'),
    
    # Account deletion
    path('account/delete/', account_views.account_delete, name='account_delete'),
    path('account/delete/confirm/', account_views.account_delete_confirm, name='account_delete_confirm'),
    
    # Password change URLs (for logged-in users)
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/password_change.html',
             success_url='/password-change/done/'
         ), 
         name='password_change'),
    path('password-change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html'
         ), 
         name='password_change_done'),
    
    # Password reset URLs (for forgotten password)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/password-reset-complete/'
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Tasks
    path('tasks/', include('tasks.urls')),
    
    # Notifications
    path('notifications/', include('notifications.urls')),

    # Use logout_then_login which accepts GET requests
    path('logout/', csrf_exempt(LogoutView.as_view(next_page='home')), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)