from django import forms


class NewUserForm(forms.Form):
    username = forms.CharField(max_length=10)
    email = forms.EmailField()
    first_name = forms.CharField(max_length=15)
    last_name = forms.CharField(max_length=25)
    password = forms.CharField(max_length=20)
