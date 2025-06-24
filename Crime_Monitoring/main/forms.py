from django import forms
from django.contrib.auth.models import User
from .models import Profile, PoliceProfile, ContactUsComplaint  

class SignupForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=[('public', 'Public'), ('police', 'Police')])

    class Meta:
        model = User
        fields = ['username', 'password']
    
class AddPoliceForm(forms.Form):
    name = forms.CharField(max_length=100)
    username = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    state = forms.CharField(max_length=100)
    district = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    station = forms.CharField(max_length=100)
    pincode = forms.CharField(max_length=10)

class ContactUsComplaintForm(forms.ModelForm):
    class Meta:
        model = ContactUsComplaint
        fields = ['name', 'contact_no', 'email', 'state', 'district', 'village', 'city', 'pincode', 'complaint']
        widgets = {
            'complaint': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your complaint'}),
        }
