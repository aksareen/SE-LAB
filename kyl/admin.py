from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from kyl.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm,AdminPasswordChangeForm

class CustomUserAdmin(UserAdmin):

    # Text to put at the end of each page's <title>.
    site_title = _('KYL admin')

    # Text to put in each page's <h1>.
    site_header = _('KYL administration')

    # Text to put at the top of the admin index page.
    index_title = _('Site administration')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email','verified_email','dob','phone','address','pincode','country')}),
        (_('Permissions'), {'fields': ('token','is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Additional Info'), {'fields': ('aadhar', 'passport',"voterid")}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('first_name','username',)
    filter_horizontal = ('groups', 'user_permissions',)


admin.site.site_header = 'KYL administration'
admin.site.register(User, CustomUserAdmin)