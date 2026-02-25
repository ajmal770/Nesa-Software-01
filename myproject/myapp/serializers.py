from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'completion_report', 'worked_hours', 'assigned_to', 'due_date', 'created_at', 'updated_at']

class TaskCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['status', 'completion_report', 'worked_hours']

    def validate(self, data):
        if data.get('status') == 'completed':
            if not data.get('completion_report') or data.get('worked_hours') is None:
                raise serializers.ValidationError(
                    "Completion report and worked hours are required when completing a task."
                )
        return data