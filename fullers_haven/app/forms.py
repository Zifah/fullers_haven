from django import forms
from app.models import BulkPlanActivation, BulkPlan

class BulkPlanActivationForm(forms.ModelForm):
    choices = ((x.id, x.name) for x in BulkPlan.objects.all() if not x.is_active)
    bulk_plan = forms.ChoiceField(choices=choices)

    def clean_bulk_plan(self):
        data = self.cleaned_data.get('bulk_plan')

        try:
            data = BulkPlan.objects.get(id=data)
        except BulkPlan.DoesNotExist:
            raise forms.ValidationError('Invalid choice for Bulk plan!!!')

        return data

    class Meta:
        model = BulkPlanActivation
        exclude = ()

