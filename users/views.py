import json
from .models import UserProfile as User

from django.db import transaction
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import View, FormView
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from .models import UserExt
from .forms import RegisterForm, LoginForm, ChangePasswordForm

from .mixins import LoginRequiredMixin



class RegisterView(View):
    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)
        return self._register(form)

    def get(self, request, *args, **kwargs):
        form = RegisterForm(request.GET)
        return self._register(form)

    def _register(self, form: RegisterForm):
        if form.is_valid():
            username = form.cleaned_data.get('username', '')
            password = form.cleaned_data.get('password', '')
            email = form.cleaned_data.get('email', '')
            try:
                with transaction.atomic():
                    user = User.objects.create_user(username=username, password=password, email=email)

                    validkey = UserExt.gen_validkey()
                    UserExt.objects.create(user=user, nickname=username, avatar='default', logintime=timezone.now(),
                                           validkey=validkey)
                    # 发送激活邮件
                    content = '欢迎注册[小智的blog], 请点击此处进行激活用户: http://127.0.0.1:8000/users/active/?username={username}&validkey={validkey}'.format(
                        username=username, validkey=validkey)
                    send_mail('[小智的blog]用户注册', content, settings.EMAIL_HOST_USER, [email])
            except Exception as e:
                return JsonResponse({'status': 500, 'errors': ['服务器错误'], 'e': e})
            return JsonResponse({'status': 200})
        else:
            return JsonResponse({'status': 400, 'errors': json.loads(form.errors.as_json()), 'result': ''})


class LoginView(FormView):
    # 指定验证表单
    form_class = LoginForm

    # 验证成功
    def form_valid(self, form):
        login(self.request, form.cached_user)
        return JsonResponse({'status': 200, 'errors': {}, 'result': {}})

    # 验证失败
    def form_invalid(self, form):
        return JsonResponse({'status': 400, 'errors': json.loads(form.errors.as_json()), 'result': {}})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect(reverse_lazy('index'))


class ActiveView(View):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username', '')
        validkey = request.GET.get('validkey', '')

        try:
            user = User.objects.get(username=username)
            if user.userext.status == 0 and user.userext.validkey != '':
                if user.userext.validkey == validkey:
                    user.userext.status = 1
                    user.userext.validkey = ''
                    user.userext.save()
                    messages.add_message(request, messages.INFO, '激活成功, 请登录')
            else:
                messages.add_message(request, messages.ERROR, '激活失败, 用户名或验证码不正确')
        except ObjectDoesNotExist as e:
            messages.add_message(request, messages.ERROR, '激活失败, 用户名不正确')

        return HttpResponseRedirect(reverse_lazy('index'))


class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = ChangePasswordForm

    # 从表单里面或者用户
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        password = form.cleaned_data.get('password', '')
        user.set_password(password)
        user.save()
        return JsonResponse({'status': 200, 'errors': {}, 'result': None})

    def form_invalid(self, form):
        return JsonResponse({'status': 400, 'errors': json.loads(form.errors.as_json()), 'result': None})
