from django import forms
from django.core.exceptions import ValidationError

from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = "__all__"

    def clean(self):
        v1 = self.cleaned_data['amount_total_min']
        v2 = self.cleaned_data['amount_total_max']
        # raise ValidationError('........')
        pass
