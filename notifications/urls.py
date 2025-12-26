from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/mark-read/', views.mark_as_read, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_notifications_read'),
    path('<int:pk>/delete/', views.delete_notification, name='delete_notification'),
    path('clear-all/', views.clear_all, name='clear_all_notifications'),
    path('count/', views.notification_count, name='notification_count'),
]