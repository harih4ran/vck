from django import forms
from django.contrib.auth.forms import UserCreationForm
from base.models import *

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields =  ['username','name','gender','age','fathersname','primary_phone','second_phone','address','business','document','photo',"password1", "password2"]
        exclude = ('password2.help_text','password1.help_text')
       
        def __init__(self, *args, **kwargs):
            super(RegisterForm, self).__init__(*args, **kwargs)

            for fieldname in ['username','name', 'password1', 'password2']:
                self.fields[fieldname].help_text = None
