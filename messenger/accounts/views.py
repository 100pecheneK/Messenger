from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import FormView
from .forms import RegisterForm, LoginForm, EditUserNames, EditUserLogin
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User


# ПРоверить пароль
# user.check_password('пароль')

@login_required()
def main(request):
    current_user = User.objects.get(username=request.user)
    all_users = User.objects.all()
    context = {
        'current_user': current_user,
        'all_users': all_users,
    }
    return render(request, 'accounts/main.html', context)


@login_required()
def settings(request):
    context = {

    }
    return render(request, 'accounts/settings.html', context)


@permission_required('polls.can_vote')
def user_management(request):
    context = {

    }
    return render(request, 'accounts/user_management.html', context)


@login_required()
def personal_settings(request):
    current_user = User.objects.get(username=request.user)
    context = {
        'current_user': current_user,
    }
    return render(request, 'accounts/personal_settings.html', context)


class EditNamesView(LoginRequiredMixin, FormView):
    form_class = EditUserNames
    page_title = 'Настройки'
    template_name = 'accounts/edit_user_names.html'

    def get(self, request):
        form = EditUserNames()
        return super(EditNamesView, self).get(request, form=form)

    def post(self, request, *args, **kwargs):
        form = EditUserNames(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            current_user = User.objects.get(username=request.user)
            current_user.first_name = data['first_name']
            current_user.last_name = data['last_name']
            current_user.save()
            return HttpResponseRedirect(reverse('accounts:settings'))

        return super(EditNamesView, self).get(request, form=form)


# class EditUserLoginView(LoginRequiredMixin, FormView):
#     form_class = EditUserLogin
#     page_title = 'Настройки'
#     template_name = 'accounts/edit_user_login.html'
#
#     def get(self, request):
#         form = EditUserLogin()
#         return super(EditUserLoginView, self).get(request, form=form)
#
#     def post(self, request, *args, **kwargs):
#         form = EditUserLogin(request.POST)
#
#         if form.is_valid():
#             data = form.cleaned_data
#             current_user = User.objects.get(username=request.user)
#             current_user.username = data['username']
#             current_user.save()
#             return HttpResponseRedirect(reverse('accounts:settings'))
#
#         return super(EditUserLoginView, self).get(request, form=form)


class RegisterView(PermissionRequiredMixin, FormView):
    permission_required = 'polls.can_vote'

    form_class = RegisterForm
    page_title = 'Register'
    template_name = 'accounts/register.html'

    def get(self, request):
        form = RegisterForm()
        return super(RegisterView, self).get(request, form=form)

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            new_profile = User.objects.create_user(
                username=data['username'],
                password=data['password'],
            )
            if new_profile:
                return HttpResponseRedirect(reverse('accounts:login'))

        return super(RegisterView, self).get(request, form=form)


class LoginView(FormView):
    form_class = LoginForm
    page_title = 'Login'
    template_name = 'accounts/login.html'

    def get(self, request):
        form = LoginForm()
        return super(LoginView, self).get(request, form=form)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect(reverse('accounts:main'))

        return super(LoginView, self).get(request, form=form)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('accounts:login'))
