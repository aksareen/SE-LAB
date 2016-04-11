from django import forms
from kyl.models import User
from django.contrib.auth import authenticate

"""
class Meta:
        model = User
        fields = ("first_name","last_name","username","email","phone","country","timezone")
        error_messages = {
            'username': {
                'max_length': "This username name is too long.",
            },
        }
        labels = {
            'username': _('Username'),
        }
        help_texts = {
            'username': _('Some useful help text.'),
        }
"""

class UserRegisterForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': "The two password fields didn't match.",
        'username_exists': "The username already exists.",
        'email_exists': "The email id is already registered.",
        'terms_unchecked' : "You haven't accepted our Terms and Conditions.",
    }
    username =  forms.CharField(min_length = 4,max_length=30,label="Username",help_text="Username",widget=forms.TextInput)
    password1 = forms.CharField(min_length= 4,required=True,label="Password",help_text="Password",widget=forms.PasswordInput)
    password2 = forms.CharField(min_length= 4,required=True,label="Password confirmation",widget=forms.PasswordInput,help_text="Enter the same password as before, for verification.")
    terms = forms.BooleanField(required=True,label="Terms and Conditions")
   
    class Meta:
        model = User
        fields = ("first_name","last_name","username","email","user_type","phone","address","pincode","dob","aadhar","passport","voterid","timezone")
        error_messages = {
            'username': {
                'max_length': "This username name is too long.",
            },
        }
    
    def __init__(self,*args,**kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs.update({
                    'placeholder': field.help_text,
                    #'required' : True,
                    'class' : "form-control",
                })

    def clean_username(self):
        username1 = self.cleaned_data.get("username")

        if User.objects.filter(username=username1).exists():
            raise forms.ValidationError(
                self.error_messages['username_exists'],
                code='username_exists',
            )
        
        return username1

    def clean_email(self):
        email1 = self.cleaned_data.get("email")

        if User.objects.filter(email=email1).exists():
            raise forms.ValidationError(
                self.error_messages['email_exists'],
                code='email_exists',
            )
        return email1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        #self.instance.username = self.cleaned_data.get('username')
        #validate_password(self.cleaned_data.get('password2'), self.instance)
        """ Validate password for validators and password strength"""
        return password2

    def clean_terms(self):
        terms1 = self.cleaned_data.get("terms")
        if not terms1:
            raise forms.ValidationError(
                self.error_messages['terms_unchecked'],
                code='terms_unchecked',
            )
        return terms1

    def save(self, commit=True):
        user = super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
