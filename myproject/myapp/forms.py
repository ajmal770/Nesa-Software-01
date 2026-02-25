from django import forms
from .models import CustomUser, Task

class UserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'assigned_admin', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=CustomUser.objects.none(), 
        label="Assign To",
        empty_label="Select a user/admin",
        widget=forms.Select(attrs={'class': 'form-select', 'style': 'padding:10px; border-radius:8px;'})
    )

    status_choices = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    status = forms.ChoiceField(
        choices=status_choices,
        widget=forms.Select(attrs={'class': 'form-select', 'style': 'padding:10px; border-radius:8px;'})
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Task Title', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Task Description', 'class': 'form-textarea'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        assigned_users = kwargs.pop('assigned_users', None)
        super().__init__(*args, **kwargs)

        if assigned_users is not None:
            self.fields['assigned_to'].queryset = assigned_users
        else:
            
            self.fields['assigned_to'].queryset = CustomUser.objects.filter(role__in=['admin', 'user'])

class TaskCompletionForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['completion_report', 'worked_hours']
        widgets = {
            'completion_report': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What did you do?'}),
            'worked_hours': forms.NumberInput(attrs={'step': 0.1, 'placeholder': 'Hours worked'}),
        }