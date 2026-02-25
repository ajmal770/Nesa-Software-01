from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('home/', views.home, name='home'),
    path('api/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('tasks/', views.user_tasks, name='user_tasks'),
    path('tasks/completed/', views.completed_tasks, name='completed_tasks'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/report/', views.TaskReportView.as_view(), name='task_report'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),

    path('panel/superadmin/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('panel/superadmin/create-user/', views.create_user, name='create_user'),
    path('panel/superadmin/edit-user/<int:id>/', views.edit_user, name='edit_user'),
    path('panel/superadmin/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('panel/superadmin/task-reports/', views.view_task_reports, name='superadmin_task_reports'),
    path('panel/superadmin/delete-task/<int:task_id>/', views.delete_task, name='delete_task'),

    path('panel/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/admin/assign-task/', views.assign_task, name='assign_task'),

    path('api/tasks/', views.UserTasksView.as_view(), name='api_user_tasks'),
    path('api/tasks/<int:id>/update/', views.UpdateTaskView.as_view(), name='api_update_task'),
    path('api/tasks/<int:id>/report/', views.TaskReportView.as_view(), name='api_task_report'),
    path('api/all-tasks/', views.AllTasksView.as_view(), name='api_all_tasks'),
]