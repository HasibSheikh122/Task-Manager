from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),

     
    # Category URLs
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/<int:pk>/delete/', views.delete_category, name='delete_category'),
    path('categories/<int:pk>/update/', views.update_category, name='update_category'),

     # Attachment URLs
    path('attachments/<int:pk>/delete/', views.delete_attachment, name='delete_attachment'),
]