from django import forms
from users.models import User
import re
class Login(forms.ModelForm):
    password = forms.CharField(
    label="Password",
    widget=forms.PasswordInput,
    min_length=6,
    max_length=128,
    help_text="Enter your password."
)
    class Meta:
        model = User
        fields = ['email']
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not re.fullmatch(r'\d{10}', password):
            raise forms.ValidationError("Password must be 6 digits or more.")
        return password
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password']
        user.set_password(password)
        if commit:
            user.save()
        return user