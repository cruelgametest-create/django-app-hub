from django.contrib.auth.views import LoginView
from django.urls import path

from .views import (
    get_cookie_view,
    set_cookie_view,
    get_session_view,
    set_session_view,
    MyLogoutPage,
    AboutMeView,
    RegisterView,
    FooBarView,
    UsersListView,
    ProfileDetailsView,
    ProfileUpdateView,
    ProfileCreateView,
    HelloView,
)

app_name = "myauth"

urlpatterns = [
    # path("login/", login_view, name="login"),
    path("login/", LoginView.as_view(template_name="myauth/login.html", redirect_authenticated_user=True), name="login"),
    # path("logout/", logout_view, name="logout"),
    path("hello/", HelloView.as_view(), name="hello"),
    path("logout/", MyLogoutPage.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("users/<int:pk>/", ProfileDetailsView.as_view(), name="profile_details"),
    path("users/", UsersListView.as_view(), name="users_list"),
    path("users/create/", ProfileCreateView.as_view(), name="profile_create"),
    path("users/<int:pk>/update/", ProfileUpdateView.as_view(), name="profile_update"),
    path("register/", RegisterView.as_view(), name="register"),
    path("cookie/get/", get_cookie_view, name="cookie-get"),
    path("cookie/set/", set_cookie_view, name="cookie-set"),
    path("session/get/", get_session_view, name="session-get"),
    path("session/set/", set_session_view, name="session-set"),
    path("foo-bar", FooBarView.as_view(), name="foo-bar")
]
