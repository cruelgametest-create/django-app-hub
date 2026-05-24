from http.client import responses
from itertools import count
from random import random

# from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView
from django.views.decorators.cache import cache_page
from django.utils.translation import gettext_lazy as _, ngettext

from .forms import ProfileForm
from .models import Profile

# class AboutMeView(TemplateView):
#     template_name = 'myauth/about-me.html'


class HelloView(View):
    welcome_message = _("welcome hello world")
    def get(self, request: HttpRequest) -> HttpResponse:
        items_str = request.GET.get("items") or 0
        items = int(items_str)
        products_line = ngettext(
            "one product",
            "{count} products",
            items,
        )
        products_line = products_line.format(count=items)
        return HttpResponse(
            f"<h1>{self.welcome_message}</h1>"
            f"\n<h2>{products_line}</h2>"
        )


class AboutMeView(UpdateView):
    model = Profile
    fields = "avatar",
    template_name_suffix = "_me_update_form"
    def get_success_url(self):
        return reverse("myauth:about-me")

    def get_object(self, queryset=None):
        return self.request.user.profile


class UsersListView(ListView):
    template_name = 'myauth/users-list.html'
    context_object_name = "users"
    queryset = User.objects.all()


class ProfileDetailsView(DetailView):
    template_name = 'myauth/user-profile.html'
    context_object_name = "profile"
    queryset = User.objects.all()


class ProfileCreateView(CreateView):
    model = Profile
    fields = "user", "bio", "avatar"
    success_url = reverse_lazy("myauth:users_list")


class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    def test_func(self):
        return self.request.user.is_staff or self.request.user == get_object_or_404(Profile, pk=self.kwargs["pk"]).user

    model = Profile
    form_class = ProfileForm
    template_name_suffix = "_update_form"
    def get_success_url(self):
        return reverse("myauth:profile_details", kwargs={"pk": self.object.user.pk})

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)

        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(request=self.request, user=user)
        return response


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('/admin/')

        return render(request, 'myauth/login.html')

    username = request.POST["username"]
    password = request.POST["password"]

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("/admin/")

    return render(request, "myauth/login.html", {"error": "Invalid login credentials"})


def logout_view(request: HttpRequest):
    logout(request)
    return redirect(reverse("myauth:login"))


class MyLogoutPage(View):
    def get(self, request):
        logout(request)
        return redirect('myauth:login')


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


@cache_page(60 * 2)  #2 min
def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r} + {random()}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
