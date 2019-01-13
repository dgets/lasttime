from django import forms


class NewUserForm(forms.Form):
    username = forms.CharField(label='User name', max_length=10)
    email = forms.EmailField(label='Email address', required=False,
                             help_text='Only required for password reset capability')
    first_name = forms.CharField(label='First name', max_length=15)
    last_name = forms.CharField(label='Last name', max_length=25)
    password = forms.CharField(label='Password', max_length=20)
