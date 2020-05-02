from django import forms
from .models import UserProfile as User
from django.core.exceptions import ObjectDoesNotExist


class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput, error_messages={'required': '用户名不能为空'})
    password = forms.CharField(widget=forms.PasswordInput, error_messages={'required': '密码不能为空'})
    password2 = forms.CharField(widget=forms.PasswordInput, error_messages={'required': '确认密码不能为空'})
    email = forms.EmailField(error_messages={'required': '邮箱不能为空', 'invalid': '邮箱格式不知正确'})

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if len(username) < 4 and len(username) > 16:
            raise forms.ValidationError('用户名长度在4-16之间')
        try:
            User.objects.get(username=username)
            raise forms.ValidationError('用户名已经存在')
        except ObjectDoesNotExist as e:
            pass

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if len(password) < 6 or len(password) > 32:
            raise forms.ValidationError('密码必须6位到32位')
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password', '')
        password2 = self.cleaned_data.get('password2', '')
        if password != password2:
            raise forms.ValidationError('两次密码不一致')

        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        try:
            User.objects.get(email=email)
            raise forms.ValidationError('邮件已注册')
        except ObjectDoesNotExist as e:
            pass

        return email


class LoginForm(forms.Form):
    username = forms.CharField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_user = None

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        username = cleaned_data.get('username', '')
        password = cleaned_data.get('password', '')
        if username == '' or password == '':
            raise forms.ValidationError('用户名或密码不能为空')
        else:
            user = None
            try:
                user = User.objects.get(username=username)
            except ObjectDoesNotExist as e:
                # 用户名不存在
                try:
                    user = User.objects.get(email=username)
                except ObjectDoesNotExist as e:
                    pass
            if user and user.check_password(password):
                if user.userext.status == 1:
                    self.cached_user = user
                elif user.userext.status == 0:
                    raise forms.ValidationError("用户未激活，请查收邮件重新激活")
            else:
                raise forms.ValidationError('用户名或密码不正确')
        return cleaned_data


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, error_messages={'required': '原密码不能为空'})
    password = forms.CharField(widget=forms.PasswordInput, error_messages={'required': '密码不能为空'})
    password2 = forms.CharField(widget=forms.PasswordInput, required=False)

    def __init__(self, user, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('原密码不正确')
        return old_password

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        if len(password) < 6 or len(password) > 32:
            raise forms.ValidationError('密码必须为6位到32位')
        return password

    def clean_password2(self):
        password = self.cleaned_data.get('password', '')
        password2 = self.cleaned_data.get('password2', '')
        if password != password2:
            raise forms.ValidationError('两次密码不一致')

        return password2
