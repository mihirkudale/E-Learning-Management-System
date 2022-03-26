from django.contrib.auth import models
from django.contrib.auth.models import User
from django.shortcuts import render
from django.urls.base import reverse_lazy
from django.views.generic.edit import FormView
from app_users.forms import UserForm, UserProfileInfoForm,User_Form,ProfileForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import REDIRECT_FIELD_NAME, authenticate, login, logout,update_session_auth_hash
from django.views.generic import TemplateView
from curriculum.models import Standard
from .models import  UserProfileInfo, Contact
from django.views.generic import CreateView,UpdateView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("ACCOUNT IS DEACTIVATED")
        else:
            messages.warning(request,'Incorrect username or password !')
            return HttpResponseRedirect(reverse('user_login'))

    else:
        return render(request, 'app_users/login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


# Create your views here.
# def index(request):
# return render(request,'app_users/index.html')

def register(request):

    registered = False

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            # user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    return render(request, 'app_users/registration.html',
                            {'registered':registered,
                             'user_form':user_form,
                             'profile_form':profile_form})

class HomeView(TemplateView):
    template_name = 'app_users/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        standards = Standard.objects.all()
        teachers = UserProfileInfo.objects.filter(user_type='teacher')
        context['standards'] = standards
        context['teachers'] = teachers
        return context

class ContactView(CreateView):
    model = Contact
    fields = '__all__'
    template_name = 'app_users/contact.html'

def change_pass(request):
    if request.method == "POST":
        changpass_form=PasswordChangeForm(user=request.user, data=request.POST)
        if changpass_form.is_valid() :
            changpass_form.save()
            messages.success(request,'Password changed Successfuly!')
            update_session_auth_hash(request, changpass_form.user)
            return HttpResponseRedirect(reverse_lazy('change_pass'))

    else:
        changpass_form=PasswordChangeForm(user=request.user)
    return render(request,'app_users/changepass.html',{'changpass_form':changpass_form})

class ViewProfile(TemplateView):
    template_name = 'app_users/profile.html'

class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    user_form = User_Form
    profile_form = ProfileForm
    template_name = 'app_users/profile-update.html'

    def post(self, request):

        post_data = request.POST or None
        file_data = request.FILES or None

        user_form = User_Form(post_data, instance=request.user)
        profile_form = ProfileForm(post_data, file_data, instance=request.user.userprofileinfo)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile was successfully updated!')
            return HttpResponseRedirect(reverse_lazy('profile'))

        context = self.get_context_data(
                                        user_form=user_form,
                                        profile_form=profile_form
                                    )

        return self.render_to_response(context)     

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)