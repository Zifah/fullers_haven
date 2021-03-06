from django import forms
from app.models import BulkPlanActivation, BulkPlan, UserProfile

#class BulkPlanActivationForm(forms.ModelForm):
#    choices = ((x.id, x.name) for x in BulkPlan.objects.all() if not x.is_active)
#    bulk_plan = forms.ChoiceField(choices=choices)

#    def clean_bulk_plan(self):
#        data = self.cleaned_data.get('bulk_plan')

#        try:
#            data = BulkPlan.objects.get(id=data)
#        except BulkPlan.DoesNotExist:
#            raise forms.ValidationError('Invalid choice for Bulk plan!!!')

#        return data

#    class Meta:
#        model = BulkPlanActivation
#        exclude = ()

class UserProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=24,)
    password = forms.CharField(max_length=24, widget=forms.PasswordInput,)
    first_name = forms.CharField(max_length=30,)
    last_name = forms.CharField(max_length=30,)
    email = forms.EmailField()
    is_staff = forms.BooleanField(required=False,)

    class Meta:
        model = UserProfile
        exclude = ('user',)

class UserProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30,)
    last_name = forms.CharField(max_length=30,)
    email = forms.EmailField()
    is_staff = forms.BooleanField(required=False,)

    class Meta:
        model = UserProfile
        exclude = ('user',)





