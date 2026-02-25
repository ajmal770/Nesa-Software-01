from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from .models import CustomUser, Task
from .forms import UserForm, TaskForm, TaskCompletionForm
from .serializers import TaskSerializer, TaskCompletionSerializer
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import render
from django.views import View
from .models import Task
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from .models import Task

@login_required
def home(request):
    return render(request, 'home.html')

class MyTokenObtainPairView(TokenObtainPairView):
    pass

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, assigned_to=request.user)
    if request.method == 'POST':
        form = TaskCompletionForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.status = 'completed'
            task.save()
            return redirect('user_tasks')
    else:
        form = TaskCompletionForm(instance=task)
    return render(request, 'complete_task.html', {'form': form, 'task': task})


@login_required
def task_reports(request):
    if request.user.role not in ['admin', 'superadmin']:
        raise PermissionDenied("You do not have permission to view reports.")
    tasks = Task.objects.filter(status='completed')
    return render(request, 'task_reports.html', {'tasks': tasks})


class UserTasksView(generics.ListAPIView):
    """
    API endpoint: List tasks for the logged-in user
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)


class UpdateTaskView(generics.UpdateAPIView):
    """
    API endpoint: Update a task (only by assigned user)
    """
    serializer_class = TaskCompletionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Task.objects.all()
    lookup_field = 'id'

    def perform_update(self, serializer):
        task = self.get_object()
        if task.assigned_to != self.request.user:
            raise PermissionDenied("You cannot update this task.")
        serializer.save()


class TaskReportView(generics.RetrieveAPIView):
    """
    API endpoint: Get completed task report (only admins or superadmin)
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Task.objects.all()
    lookup_field = 'id'

    def get_object(self):
        task = super().get_object()
        if self.request.user.role not in ['admin', 'superadmin']:
            raise PermissionDenied("Only Admins or SuperAdmins can view reports.")
        if task.status != 'completed':
            raise PermissionDenied("Only completed tasks have reports.")
        return task


class TaskListView(APIView):
    """
    API endpoint: List tasks for the logged-in user (JWT)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        tasks = Task.objects.filter(assigned_to=user)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class AllTasksView(APIView):
    """
    API endpoint: List all tasks (superadmin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if request.user.role != 'superadmin':
            raise PermissionDenied("Only superadmin can view all tasks.")
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

@login_required
def superadmin_dashboard(request):                                       

    if request.user.role != 'superadmin' and not request.user.is_superuser:
        raise PermissionDenied

    users = CustomUser.objects.all()

    return render(request, 'superadmin_dashboard.html', {
        'users': users
    })


@login_required
def create_user(request):

    print("Logged in user:", request.user)
    print("Is superuser:", request.user.is_superuser)
    print("Role:", request.user.role)
    
    if request.user.role != 'superadmin' and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('superadmin_dashboard')
    else:
        form = UserForm()

    return render(request, 'create_user.html', {'form': form})

@login_required
def delete_user(request, user_id):

    if not request.user.is_superuser:
        raise PermissionDenied

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        user.delete()
        return redirect('superadmin_dashboard')

    return render(request, "confirm_delete.html", {"user": user})


@login_required
def view_task_reports(request):
    if request.user.role != 'superadmin':
        return redirect('admin_dashboard')
    tasks = Task.objects.filter(status='completed')
    return render(request, 'task_reports.html', {'tasks': tasks})



@login_required
def admin_dashboard(request):
    if request.user.role not in ['admin', 'superadmin']:
        raise PermissionDenied("Only Admin allowed.")

    if request.user.role == 'admin':
        users = request.user.assigned_users.all()
        tasks = Task.objects.filter(assigned_to__in=users)
    else:
        users = CustomUser.objects.all()
        tasks = Task.objects.all()

    return render(request, 'admin_dashboard.html', {
        'users': users,
        'tasks': tasks
    })


@login_required
def assign_task(request):
    if request.user.role != 'admin':
        raise PermissionDenied("Only Admin allowed.")

    users_and_admins = CustomUser.objects.filter(role__in=['user', 'admin'])

    if request.method == 'POST':
        form = TaskForm(request.POST, assigned_users=users_and_admins)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = TaskForm(assigned_users=users_and_admins)

    return render(request, 'assign_task.html', {'form': form})

def check_permission(user, task=None):
    if user.role == 'superadmin':
        return True
    elif user.role == 'admin':
        if task and task.assigned_to.assigned_admin != user:
            raise PermissionDenied("You cannot access this task.")
        return True
    elif user.role == 'user':
        if task and task.assigned_to != user:
            raise PermissionDenied("You can only access your own tasks.")
        return True
    else:
        raise PermissionDenied("Invalid role.")

from django.core.exceptions import PermissionDenied

def superadmin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.role != 'superadmin':
            raise PermissionDenied("Only SuperAdmin allowed.")
        return view_func(request, *args, **kwargs)
    return wrapper



@login_required
def edit_user(request, id):

    if request.user.role != 'superadmin' and not request.user.is_superuser:
        raise PermissionDenied

    user = get_object_or_404(CustomUser, id=id)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('superadmin_dashboard')
    else:
        form = UserForm(instance=user)

    return render(request, 'superadmin.html', {'form': form})



@login_required
def user_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user).exclude(status='completed')
    return render(request, 'tasks.html', {'tasks': tasks})


@login_required
def completed_tasks(request):
    
    tasks = Task.objects.filter(assigned_to=request.user, status='completed')
    return render(request, 'completed_tasks.html', {'tasks': tasks})

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        raise PermissionDenied("Only Admin allowed.")
    
    tasks = Task.objects.all().order_by('-created_at')
    users = CustomUser.objects.all()

    context = {
        'users': users,
        'tasks': tasks
    }

    return render(request, 'admin_dashboard.html', context)     

@login_required
def my_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    
    context = {
        'tasks': tasks
    }
    return render(request, 'my_tasks.html', context)

def admin_dashboard(request):
    users = CustomUser.objects.all()
    tasks = Task.objects.all()

    if request.method == "POST":
        title = request.POST.get('title')
        user_id = request.POST.get('assigned_to')
        assigned_user = CustomUser.objects.get(id=user_id)
        Task.objects.create(title=title, assigned_to=assigned_user)
        return redirect('admin_dashboard')

    return render(request, 'admin_dashboard.html', {'users': users, 'tasks': tasks})

@login_required
def assign_task(request):
    if request.user.role != 'admin':
        raise PermissionDenied("Only Admin allowed.")

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            return redirect('admin_dashboard')
    else:
        form = TaskForm()
        form.fields['assigned_to'].queryset = CustomUser.objects.filter(manager=request.user)

    context = {
        'form': form
    }
    return render(request, 'assign_task.html', context)


class UserTasksView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'user_tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user).order_by('-created_at')

class UpdateTaskView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'update_task.html'
    pk_url_kwarg = 'id'

class TaskReportView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task_report.html'
    pk_url_kwarg = 'id'

@login_required
def completed_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user, completed=True)
    return render(request, 'completed_tasks.html', {'tasks': tasks})




def assign_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard') 
    else:
        form = TaskForm()
    
 
    return render(request, 'assign_task.html', {'form': form})


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect('superadmin_dashboard')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    return redirect('superadmin_dashboard')

class TaskReportView(View):
    def get(self, request, task_id):
   
        task = get_object_or_404(Task, id=task_id)
        return render(request, 'task_report.html', {'task': task})
    


class UserTasksView(ListView):
    model = Task
    template_name = 'user_tasks.html' 
    context_object_name = 'tasks'

class UserTasksView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'user_tasks.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user).order_by('-created_at')



# def user_tasks(request):
#     tasks = Task.objects.all()
#     return render(request, 'myapp/tasks.html', {'tasks': tasks})
