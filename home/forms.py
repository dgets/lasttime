from django import forms

from lasttime.myglobals import Const


class NewUserForm(forms.Form):
    username = forms.CharField(label='User name', max_length=10)
    email = forms.EmailField(label='Email address', required=False,
                             help_text='Only required for password reset capability')
    first_name = forms.CharField(label='First name', max_length=15)
    last_name = forms.CharField(label='Last name', max_length=25)
    tz = forms.CharField(label='Local time zone', max_length=20, initial=Const.Time_Zone)
    password = forms.CharField(label='Password', max_length=20)
